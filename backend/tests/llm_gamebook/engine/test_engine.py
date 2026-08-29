from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from openai import OpenAIError
from pydantic_ai import (
    AgentRunError,
    ModelAPIError,
    ModelHTTPError,
    ModelMessage,
    ModelRequest,
    RunContext,
    RunUsage,
    ToolDefinition,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import create_messages, get_messages
from llm_gamebook.db.crud.session import get_session as get_session_crud
from llm_gamebook.db.crud.session import mark_session_ended
from llm_gamebook.db.models import Session
from llm_gamebook.db.models.message import Message, MessageKind
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.db.models.user_settings import UserSettings
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.message import (
    ContentDelta,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
)
from llm_gamebook.engine.session_adapter import SessionAdapter
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.errors import DynamicFieldEvalError, SessionEndedError
from llm_gamebook.story.schemas import Project, ProjectSource
from llm_gamebook.story.state import SessionStateData
from llm_gamebook.story.traits.graph import GraphTransitionAction

from .conftest import EngineErrorMessages, EngineMessages, StreamMessages


async def test_story_engine_generate_response_streaming(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_messages: EngineMessages,
    engine_error_messages: EngineErrorMessages,
    stream_messages: StreamMessages,
    session: Session,
) -> None:
    chunks = ("Stream", "ing", " re", "sponse", " from", " Function", "Model")

    async def stream_function(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        for chunk in chunks:
            yield chunk

    func_model = FunctionModel(stream_function=stream_function)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)

    assert len(engine_messages) == 2
    start_message, stop_message = engine_messages
    assert isinstance(start_message, ResponseStartedMessage)
    assert start_message.session_id == session.id
    assert isinstance(stop_message, ResponseStoppedMessage)
    assert stop_message.session_id == session.id
    assert len(engine_error_messages) == 0

    # 1 request
    # 1 response
    # 1 part
    # 6 deltas
    assert len(stream_messages) == 9

    # Request
    req_message = stream_messages[0]
    assert isinstance(req_message, StreamMessageMessage)
    req = req_message.message
    assert req.session_id == session.id
    assert req.kind == MessageKind.REQUEST

    # Response
    resp_message = stream_messages[1]
    assert isinstance(resp_message, StreamMessageMessage)
    resp = resp_message.message
    assert resp.session_id == session.id
    assert resp.kind == MessageKind.RESPONSE

    # Part
    part_message = stream_messages[2]
    assert isinstance(part_message, StreamPartMessage)
    part = part_message.part
    assert part.message_id == resp.id
    assert part.kind == PartKind.TEXT
    assert part.content == chunks[0]

    # Deltas
    for idx in range(3, len(chunks) + 1):
        delta_message = stream_messages[idx]
        assert isinstance(delta_message, StreamPartDeltaMessage)
        assert delta_message.session_id == session.id
        assert delta_message.message_id == resp.id
        assert delta_message.part_id == part.id
        delta = delta_message.delta
        assert isinstance(delta, ContentDelta)
        assert delta.content == chunks[idx - 2]


@pytest.mark.parametrize(
    "error",
    [
        httpx.RequestError("Network error", request=None),
        OpenAIError(),
        AgentRunError("Agent run failed"),
        ModelAPIError("test", "Model API error"),
        ModelHTTPError(500, "ModelName", body={"message": "HTTP error"}),
    ],
)
async def test_story_engine_generate_response_error(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_messages: EngineMessages,
    engine_error_messages: EngineErrorMessages,
    session: Session,
    error: Exception,
) -> None:
    async def mock_fail_stream(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "error"  # Yield first to make it a proper async generator
        raise error

    error_model = FunctionModel(stream_function=mock_fail_stream)
    story_engine.set_model(error_model)

    await story_engine.generate_response(db_session)

    assert len(engine_messages) == 2
    start_message, stop_message = engine_messages
    assert isinstance(start_message, ResponseStartedMessage)
    assert start_message.session_id == session.id
    assert isinstance(stop_message, ResponseStoppedMessage)
    assert stop_message.session_id == session.id

    assert len(engine_error_messages) == 1
    assert isinstance(engine_error_messages[0].error, type(error))


def _broken_dynamic_field_project_data() -> dict[str, object]:
    return {
        "id": "test/dyn-engine",
        "source": ProjectSource.LOCAL,
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "Player",
                "name": "Player",
                "instructions": "Player data.",
                "traits": ["described"],
                "entities": [
                    {
                        "id": "player",
                        "name": "Player",
                        "description": "=player.nonexistent + 1",
                    }
                ],
            }
        ],
    }


async def test_generate_response_surfaces_dynamic_field_eval_error(
    db_session: AsyncDbSession,
    session: Session,
    message_bus: MessageBus,
    test_model: TestModel,
    engine_error_messages: EngineErrorMessages,
) -> None:
    """A dynamic field that fails at runtime fails the step, naming field + expression."""
    project = Project.from_data(_broken_dynamic_field_project_data())
    context = StoryContext(project)
    story_engine = StoryEngine(session.id, test_model, context, message_bus, stream_debounce=0.0)

    await story_engine.generate_response(db_session)

    assert len(engine_error_messages) == 1
    error = engine_error_messages[0].error
    assert isinstance(error, DynamicFieldEvalError), f"unexpected error: {error!r}"
    assert error.field == "player.description"
    assert error.source == "=player.nonexistent + 1"
    message = str(error)
    assert "player.description" in message
    assert "=player.nonexistent + 1" in message


async def test_set_model_replaces_agent(story_engine: StoryEngine, test_model: TestModel) -> None:
    assert story_engine._agent is not None
    assert story_engine._agent.model is test_model

    new_model = TestModel(custom_output_text="New model response")
    story_engine.set_model(new_model)

    assert story_engine._agent.model is new_model


async def test_set_model_preserves_(story_engine: StoryEngine, story_context: StoryContext) -> None:
    new_model = TestModel(custom_output_text="New model response")

    story_engine.set_model(new_model)

    assert story_engine._context is story_context


async def test_set_model_preserves_tools(
    story_engine: StoryEngine, story_context: StoryContext
) -> None:
    new_model = TestModel(custom_output_text="New model response")

    story_engine.set_model(new_model)

    assert story_engine._agent is not None
    assert story_engine._agent.deps_type is StoryContext


async def test_set_model_uses_same_prepare_tools(
    story_engine: StoryEngine, story_context: StoryContext
) -> None:
    new_model = TestModel(custom_output_text="New model response")

    story_engine.set_model(new_model)

    assert story_engine._agent is not None
    assert story_engine._agent._prepare_tools == story_engine._prepare_tools


async def test_set_model_creates_new_agent_instance(story_engine: StoryEngine) -> None:
    original_agent = story_engine._agent
    new_model = TestModel(custom_output_text="New model response")

    story_engine.set_model(new_model)

    assert story_engine._agent is not original_agent


async def test_set_model_allows_subsequent_requests_with_new_model(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_messages: EngineMessages,
    engine_error_messages: EngineErrorMessages,
    session: Session,
) -> None:
    new_model = TestModel(custom_output_text="Response from new model")
    story_engine.set_model(new_model)

    await story_engine.generate_response(db_session)

    assert len(engine_messages) == 2
    start_message, stop_message = engine_messages
    assert isinstance(start_message, ResponseStartedMessage)
    assert start_message.session_id == session.id
    assert isinstance(stop_message, ResponseStoppedMessage)
    assert stop_message.session_id == session.id
    assert len(engine_error_messages) == 0


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [
            ModelRequest(parts=[UserPromptPart(content="First")]),
        ],
        [
            ModelRequest(parts=[UserPromptPart(content="First")]),
            ModelRequest(parts=[UserPromptPart(content="Second")]),
        ],
    ],
)
async def test_prepare_tools_returns_none_for_intro(
    story_engine: StoryEngine, story_context: StoryContext, messages: list[ModelMessage]
) -> None:
    tools = [ToolDefinition(name="Foo")]
    ctx = RunContext(deps=story_context, model=TestModel(), usage=RunUsage(), messages=messages)

    result = await story_engine._prepare_tools(ctx, tools)

    assert result is None


async def test_prepare_tools_returns_tools_for_conversation(
    story_engine: StoryEngine, story_context: StoryContext
) -> None:
    tools = [ToolDefinition(name="Foo")]

    messages: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="First")]),
        ModelRequest(parts=[UserPromptPart(content="Second")]),
        ModelRequest(parts=[UserPromptPart(content="Third")]),
    ]
    ctx = RunContext(deps=story_context, model=TestModel(), usage=RunUsage(), messages=messages)

    result = await story_engine._prepare_tools(ctx, tools)

    assert result is not None
    assert len(result) == len(tools)


async def test_state_persists_after_response(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_error_messages: EngineErrorMessages,
) -> None:
    action = GraphTransitionAction(entity_id="main", to="spark_of_hope")
    story_engine._context.store.dispatch(action)

    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)

    assert len(engine_error_messages) == 0

    loaded_state = await story_engine.session_adapter.load_state(db_session)
    assert loaded_state is not None
    main_entity = loaded_state.entities["main"]
    current_node_id = main_entity["current_node_id"]
    assert current_node_id == "spark_of_hope"


async def test_generate_response_persists_response_messages(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    session: Session,
) -> None:
    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "First response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    count_before = await story_engine.session_adapter.get_message_count(db_session)
    await story_engine.generate_response(db_session)
    count_after = await story_engine.session_adapter.get_message_count(db_session)

    assert count_before == 0
    assert count_after == 2

    messages = [msg async for msg in story_engine.session_adapter.get_message_history(db_session)]
    assert len(messages) == 2
    assert messages[0].kind == "request"
    assert messages[1].kind == "response"


async def test_generate_response_first_run_has_intro_message(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    session: Session,
) -> None:
    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response with intro"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)

    messages = [msg async for msg in story_engine.session_adapter.get_message_history(db_session)]
    assert len(messages) == 2
    assert isinstance(messages[0], ModelRequest)
    intro_content = "".join(
        part.content
        for part in messages[0].parts
        if hasattr(part, "content") and isinstance(part.content, str)
    )
    assert "Write the opening of the story" in intro_content


async def test_generate_response_no_duplicate_messages_after_multiple_calls(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    session: Session,
) -> None:
    call_count = 0

    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        nonlocal call_count
        call_count += 1
        if messages and messages[-1].parts:
            first_part = messages[-1].parts[0]
            if isinstance(first_part, UserPromptPart):
                yield f"Response {first_part.content}"
            else:
                yield "Response"
        else:
            yield "Response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)
    count_after_first = await story_engine.session_adapter.get_message_count(db_session)

    await story_engine.generate_response(db_session)
    count_after_second = await story_engine.session_adapter.get_message_count(db_session)

    assert count_after_first == 2
    assert count_after_second == 3


async def test_generate_response_does_not_persist_input_request_messages(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    session: Session,
) -> None:
    adapter = SessionAdapter(session.id, story_engine._context, story_engine._bus)
    await adapter.create_user_request(db_session, "User input")

    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    count_before = await story_engine.session_adapter.get_message_count(db_session)
    await story_engine.generate_response(db_session)
    count_after = await story_engine.session_adapter.get_message_count(db_session)

    assert count_before == 1
    assert count_after == 2

    messages = [msg async for msg in story_engine.session_adapter.get_message_history(db_session)]
    request_messages = [m for m in messages if m.kind == "request"]
    response_messages = [m for m in messages if m.kind == "response"]
    assert len(request_messages) == 1
    assert len(response_messages) == 1


async def test_generate_response_blocked_on_ended_session(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    session: Session,
    engine_messages: EngineMessages,
    engine_error_messages: EngineErrorMessages,
) -> None:
    await mark_session_ended(db_session, session.id)

    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)

    # No messages are created for an ended session
    assert await story_engine.session_adapter.get_message_count(db_session) == 0

    # Started + stopped are still published, plus an error message
    assert len(engine_messages) == 2
    assert isinstance(engine_messages[0], ResponseStartedMessage)
    assert isinstance(engine_messages[1], ResponseStoppedMessage)
    assert len(engine_error_messages) == 1
    assert isinstance(engine_error_messages[0].error, SessionEndedError)


async def test_current_state_persisted_to_session_row(
    story_engine: StoryEngine, db_session: AsyncDbSession, session: Session
) -> None:
    action = GraphTransitionAction(entity_id="main", to="spark_of_hope")
    story_engine._context.store.dispatch(action)

    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)

    loaded = await get_session_crud(db_session, session.id)
    assert loaded is not None
    assert loaded.state is not None
    data = SessionStateData.model_validate(loaded.state)
    assert data.entities["main"]["current_node_id"] == "spark_of_hope"


async def test_response_state_save_triggers_history_cleanup(
    story_engine: StoryEngine, db_session: AsyncDbSession, session: Session
) -> None:
    settings = UserSettings(id="settings", max_state_history=2)
    db_session.add(settings)
    await db_session.commit()

    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    seeded_states: list[dict[str, object]] = [
        {"entities": {"main": {"current_node_id": f"node_{i}"}}} for i in range(3)
    ]
    seeded = [
        Message(
            kind=MessageKind.RESPONSE,
            session_id=session.id,
            timestamp=base + timedelta(minutes=i),
            state=state,
        )
        for i, state in enumerate(seeded_states)
    ]
    await create_messages(db_session, seeded)

    story_engine._context.store.dispatch(
        GraphTransitionAction(entity_id="main", to="spark_of_hope")
    )

    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response"

    func_model = FunctionModel(stream_function=stream_fn)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session)

    messages = await get_messages(db_session, session.id)
    # 3 seeded + 1 new response = 4 snapshots; limit 2 removes the 2 oldest
    assert [m.state for m in messages] == [None, None, seeded_states[2], messages[3].state]
    assert messages[3].state is not None

    loaded = await get_session_crud(db_session, session.id)
    assert loaded is not None
    data = SessionStateData.model_validate(loaded.state or {})
    assert data.entities["main"]["current_node_id"] == "spark_of_hope"
