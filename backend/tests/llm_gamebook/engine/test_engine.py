from collections.abc import AsyncIterator

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

from llm_gamebook.db.models import Session
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.message import (
    ContentDelta,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
)
from llm_gamebook.story.context import StoryContext
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
