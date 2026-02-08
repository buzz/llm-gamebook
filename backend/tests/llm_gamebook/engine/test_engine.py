from collections.abc import AsyncIterator
from typing import NoReturn
from uuid import UUID

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
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.message import ResponseErrorBusMessage, StreamUpdateBusMessage
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import StoryState

type EngineEvents = tuple[list[str], list[ResponseErrorBusMessage]]
type StreamEvents = list[StreamUpdateBusMessage]


@pytest.fixture
def engine_events(message_bus: MessageBus) -> EngineEvents:
    events: list[str] = []
    error_events: list[ResponseErrorBusMessage] = []

    def track_started(session_id: object) -> None:
        assert isinstance(session_id, UUID)
        events.append("started")

    def track_stopped(session_id: object) -> None:
        assert isinstance(session_id, UUID)
        events.append("stopped")

    def track_error(msg: object) -> None:
        assert isinstance(msg, ResponseErrorBusMessage)
        error_events.append(msg)

    message_bus.subscribe("engine.response.started", track_started)
    message_bus.subscribe("engine.response.stopped", track_stopped)
    message_bus.subscribe("engine.response.error", track_error)

    return events, error_events


@pytest.fixture
def stream_events(message_bus: MessageBus) -> StreamEvents:
    events: StreamEvents = []

    def track_stream(msg: object) -> None:
        assert isinstance(msg, StreamUpdateBusMessage)
        events.append(msg)

    message_bus.subscribe("engine.response.stream", track_stream)

    return events


async def test_story_engine_generate_response_streaming(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_events: EngineEvents,
    stream_events: StreamEvents,
    session: Session,
) -> None:
    events, error_events = engine_events

    chunks = ("Stream", "ing", " re", "sponse", " from", " Functio", "Model")

    async def stream_function(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        for chunk in chunks:
            yield chunk

    func_model = FunctionModel(stream_function=stream_function)
    story_engine.set_model(func_model)

    await story_engine.generate_response(db_session, streaming=True)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 0
    assert len(stream_events) == 8

    for stream_event in stream_events:
        assert stream_event.session_id == story_engine.session_adapter.session_id
        assert stream_event.response_id is not None
        assert len(stream_event.part_ids) > 0

    assert stream_events[0].response.text == "Stream"
    assert stream_events[1].response.text == "Streaming"
    assert stream_events[2].response.text == "Streaming re"
    assert stream_events[3].response.text == "Streaming response"
    assert stream_events[4].response.text == "Streaming response from"
    assert stream_events[5].response.text == "Streaming response from Functio"
    assert stream_events[6].response.text == "Streaming response from FunctioModel"
    assert stream_events[7].response.text == "Streaming response from FunctioModel"


async def test_story_engine_generate_response_non_streaming(
    story_engine: StoryEngine, db_session: AsyncDbSession, engine_events: EngineEvents
) -> None:
    events, error_events = engine_events
    await story_engine.generate_response(db_session, streaming=False)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 0


async def test_story_engine_generate_response_error_httpx(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_events: EngineEvents,
    session: Session,
) -> None:
    events, error_events = engine_events

    def mock_fail_function(messages: list[ModelMessage], info: AgentInfo) -> NoReturn:
        msg = "Network error"
        raise httpx.RequestError(msg, request=None)

    error_model = FunctionModel(function=mock_fail_function)
    story_engine.set_model(error_model)

    await story_engine.generate_response(db_session, streaming=False)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 1
    assert isinstance(error_events[0].error, httpx.RequestError)


async def test_story_engine_generate_response_error_openai(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_events: EngineEvents,
    session: Session,
) -> None:
    events, error_events = engine_events

    def mock_fail_function(messages: list[ModelMessage], info: AgentInfo) -> NoReturn:
        raise OpenAIError

    error_model = FunctionModel(function=mock_fail_function)
    story_engine.set_model(error_model)

    await story_engine.generate_response(db_session, streaming=False)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 1
    assert isinstance(error_events[0].error, OpenAIError)


async def test_story_engine_generate_response_error_agent_run(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_events: EngineEvents,
    session: Session,
) -> None:
    events, error_events = engine_events

    def mock_fail_function(messages: list[ModelMessage], info: AgentInfo) -> NoReturn:
        msg = "Agent run failed"
        raise AgentRunError(msg)

    error_model = FunctionModel(function=mock_fail_function)
    story_engine.set_model(error_model)

    await story_engine.generate_response(db_session, streaming=False)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 1
    assert isinstance(error_events[0].error, AgentRunError)


async def test_story_engine_generate_response_error_model_api(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_events: EngineEvents,
    session: Session,
) -> None:
    events, error_events = engine_events

    def mock_fail_function(messages: list[ModelMessage], info: AgentInfo) -> NoReturn:
        model_name = "test"
        raise ModelAPIError(model_name, "Model API error")

    error_model = FunctionModel(function=mock_fail_function)
    story_engine.set_model(error_model)

    await story_engine.generate_response(db_session, streaming=False)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 1
    assert isinstance(error_events[0].error, ModelAPIError)


async def test_story_engine_generate_response_error_model_http(
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
    engine_events: EngineEvents,
    session: Session,
) -> None:
    events, error_events = engine_events

    def mock_fail_function(messages: list[ModelMessage], info: AgentInfo) -> NoReturn:
        raise ModelHTTPError(500, "ModelName", body={"message": "HTTP error"})

    error_model = FunctionModel(function=mock_fail_function)
    story_engine.set_model(error_model)

    await story_engine.generate_response(db_session, streaming=False)

    assert "started" in events
    assert "stopped" in events
    assert len(error_events) == 1
    assert isinstance(error_events[0].error, ModelHTTPError)


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
    story_engine: StoryEngine, story_state: StoryState, messages: list[ModelMessage]
) -> None:
    tools = [ToolDefinition(name="Foo")]
    ctx = RunContext(deps=story_state, model=TestModel(), usage=RunUsage(), messages=messages)

    result = await story_engine._prepare_tools(ctx, tools)

    assert result is None


async def test_prepare_tools_returns_tools_for_conversation(
    story_engine: StoryEngine, story_state: StoryState
) -> None:
    tools = [ToolDefinition(name="Foo")]

    messages: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="First")]),
        ModelRequest(parts=[UserPromptPart(content="Second")]),
        ModelRequest(parts=[UserPromptPart(content="Third")]),
    ]
    ctx = RunContext(deps=story_state, model=TestModel(), usage=RunUsage(), messages=messages)

    result = await story_engine._prepare_tools(ctx, tools)

    assert result is not None
    assert len(result) == len(tools)
