from uuid import uuid4

import pytest
from pydantic_ai import Agent

from llm_gamebook.engine._runner import StreamRunner
from llm_gamebook.engine.message import (
    ResponseErrorMessage,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    ResponseStreamUpdateMessage,
)
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import StoryState

type EngineEvents = tuple[list[str], list[ResponseErrorMessage]]
type StreamEvents = list[ResponseStreamUpdateMessage]


@pytest.fixture
def engine_events(message_bus: MessageBus) -> EngineEvents:
    events: list[str] = []
    error_events: list[ResponseErrorMessage] = []

    def track_started(msg: ResponseStartedMessage) -> None:
        events.append("started")

    def track_stopped(msg: ResponseStoppedMessage) -> None:
        events.append("stopped")

    def track_error(msg: ResponseErrorMessage) -> None:
        error_events.append(msg)

    message_bus.subscribe(ResponseStartedMessage, track_started)
    message_bus.subscribe(ResponseStoppedMessage, track_stopped)
    message_bus.subscribe(ResponseErrorMessage, track_error)

    return events, error_events


@pytest.fixture
def stream_events(message_bus: MessageBus) -> StreamEvents:
    events: StreamEvents = []

    def track_stream(msg: ResponseStreamUpdateMessage) -> None:
        events.append(msg)

    message_bus.subscribe(ResponseStreamUpdateMessage, track_stream)

    return events


@pytest.fixture
async def stream_runner(
    message_bus: MessageBus, test_agent: Agent[StoryState, str]
) -> StreamRunner:
    session_id = uuid4()
    return StreamRunner(test_agent, session_id, message_bus, debounce=0.0)
