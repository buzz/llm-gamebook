from collections.abc import Sequence
from dataclasses import replace
from uuid import uuid4

import pytest
from pydantic_ai import Agent

from llm_gamebook.db.models.message import Message
from llm_gamebook.db.models.part import Part
from llm_gamebook.engine._runner import StreamRunner
from llm_gamebook.engine.message import (
    ResponseErrorMessage,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
)
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.context import StoryContext

type EngineMessage = ResponseStartedMessage | ResponseStoppedMessage
type EngineMessages = Sequence[EngineMessage]
type EngineErrorMessages = Sequence[ResponseErrorMessage]
type StreamMessage = StreamMessageMessage | StreamPartMessage | StreamPartDeltaMessage
type StreamMessages = Sequence[StreamMessage]


@pytest.fixture
def engine_messages(message_bus: MessageBus) -> EngineMessages:
    events: list[EngineMessage] = []

    def track_started(msg: ResponseStartedMessage) -> None:
        events.append(msg)

    def track_stopped(msg: ResponseStoppedMessage) -> None:
        events.append(msg)

    message_bus.subscribe(ResponseStartedMessage, track_started)
    message_bus.subscribe(ResponseStoppedMessage, track_stopped)

    return events


@pytest.fixture
def engine_error_messages(message_bus: MessageBus) -> EngineErrorMessages:
    error_events: list[ResponseErrorMessage] = []

    def track_error(msg: ResponseErrorMessage) -> None:
        error_events.append(msg)

    message_bus.subscribe(ResponseErrorMessage, track_error)

    return error_events


@pytest.fixture
def stream_messages(message_bus: MessageBus) -> StreamMessages:
    events: list[StreamMessage] = []

    def track_message(msg: StreamMessageMessage) -> None:
        message = Message(**msg.message.model_dump())
        snapshot = replace(msg, message=message)
        events.append(snapshot)

    def track_part(msg: StreamPartMessage) -> None:
        part = Part(**msg.part.model_dump())
        snapshot = replace(msg, part=part)
        events.append(snapshot)

    def track_part_delta(msg: StreamPartDeltaMessage) -> None:
        events.append(msg)

    message_bus.subscribe(StreamMessageMessage, track_message)
    message_bus.subscribe(StreamPartMessage, track_part)
    message_bus.subscribe(StreamPartDeltaMessage, track_part_delta)

    return events


@pytest.fixture
async def stream_runner(
    message_bus: MessageBus, test_agent: Agent[StoryContext, str]
) -> StreamRunner:
    session_id = uuid4()
    return StreamRunner(test_agent, session_id, message_bus, debounce=0.0)
