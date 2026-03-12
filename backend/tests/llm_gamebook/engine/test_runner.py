from typing import assert_never
from uuid import UUID, uuid4

from pydantic_ai import Agent, ModelMessage, ModelRequest, UserPromptPart

from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.engine._runner import StreamRunner
from llm_gamebook.engine.message import (
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
)
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.context import StoryContext

from .conftest import StreamMessages


async def test_stream_runner_run_returns_messages(
    stream_runner: StreamRunner, story_context: StoryContext
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Hello")])]

    result = await stream_runner.run(messages, story_context)

    result_messages = list(result)
    assert len(result_messages) > 0


async def test_stream_runner_handles_model_request_node(
    stream_runner: StreamRunner,
    story_context: StoryContext,
    stream_messages: StreamMessages,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test prompt")])]

    await stream_runner.run(messages, story_context)

    assert len(stream_messages) >= 1
    message = stream_messages[0]
    assert isinstance(message, StreamMessageMessage)
    assert message.message.id is not None


async def test_stream_runner_handles_part_start_event(
    stream_runner: StreamRunner,
    story_context: StoryContext,
    stream_messages: StreamMessages,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_context)

    assert len(stream_messages) >= 1
    message = stream_messages[0]
    assert message.session_id == stream_runner._session_id
    assert isinstance(message, StreamMessageMessage)
    assert message.message is not None


async def test_stream_runner_handles_part_delta_event(
    stream_runner: StreamRunner,
    story_context: StoryContext,
    stream_messages: StreamMessages,
) -> None:
    message_count, part_count, delta_count = 0, 0, 0
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_context)

    assert len(stream_messages) >= 1
    for message in stream_messages:
        assert message.session_id == stream_runner._session_id

        if isinstance(message, StreamMessageMessage):
            assert message.session_id is not None
            assert message.message.id is not None
            message_count += 1
        elif isinstance(message, StreamPartMessage):
            assert message.session_id is not None
            assert message.part.id is not None
            part_count += 1
        elif isinstance(message, StreamPartDeltaMessage):
            assert message.session_id is not None
            assert message.message_id is not None
            assert message.part_id is not None
            delta_count += 1
        else:
            assert_never(message)

    assert message_count == 4
    assert part_count == 4
    assert delta_count >= 1


async def test_stream_runner_multiple_responses(
    stream_runner: StreamRunner,
    story_context: StoryContext,
    stream_messages: StreamMessages,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="First")])]

    result1 = await stream_runner.run(messages, story_context)
    result1_list = list(result1)

    messages2: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="Second")]),
    ]

    result2 = await stream_runner.run(messages2, story_context)
    result2_list = list(result2)

    total_responses = len(result1_list) + len(result2_list)
    assert total_responses >= 1


async def test_stream_runner_debounce_reduces_events(
    message_bus: MessageBus, story_context: StoryContext, test_agent: Agent[StoryContext, str]
) -> None:
    session_id = uuid4()
    runner = StreamRunner(test_agent, session_id, message_bus, debounce=0.5)

    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    events: list[StreamMessageMessage] = []

    def track_stream(msg: StreamMessageMessage) -> None:
        events.append(msg)

    message_bus.subscribe(StreamMessageMessage, track_stream)

    await runner.run(messages, story_context)

    assert len(events) > 0
    assert len(events) <= 4


async def test_stream_runner_zero_debounce_produces_more_events(
    message_bus: MessageBus, story_context: StoryContext, test_agent: Agent[StoryContext, str]
) -> None:
    session_id = uuid4()
    runner_zero = StreamRunner(test_agent, session_id, message_bus, debounce=0.0)

    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    events: list[StreamMessageMessage] = []

    def track_stream(msg: StreamMessageMessage) -> None:
        events.append(msg)

    message_bus.subscribe(StreamMessageMessage, track_stream)

    await runner_zero.run(messages, story_context)

    assert len(events) >= 1


async def test_stream_runner_response_id_is_uuid(
    stream_runner: StreamRunner, story_context: StoryContext
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    result = await stream_runner.run(messages, story_context)

    for msg in result:
        assert isinstance(msg.id, UUID)


async def test_stream_runner_part_ids_are_uuids(
    stream_runner: StreamRunner, story_context: StoryContext
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    result = await stream_runner.run(messages, story_context)

    for msg in result:
        for part in msg.parts:
            assert isinstance(part.id, UUID)


async def test_stream_runner_session_id_matches(
    stream_runner: StreamRunner, story_context: StoryContext, stream_messages: StreamMessages
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_context)

    for message in stream_messages:
        assert message.session_id == stream_runner._session_id


async def test_stream_runner_run_returns_only_response_messages(
    stream_runner: StreamRunner, story_context: StoryContext
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    result = await stream_runner.run(messages, story_context)

    result_messages = list(result)
    assert len(result_messages) >= 1
    for msg in result_messages:
        assert msg.kind == MessageKind.RESPONSE


async def test_stream_runner_messages_contains_only_responses(
    stream_runner: StreamRunner, story_context: StoryContext
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_context)

    assert len(stream_runner._messages) >= 1
    for msg in stream_runner._messages:
        assert msg.kind == MessageKind.RESPONSE


async def test_stream_runner_does_not_store_request_messages(
    stream_runner: StreamRunner, story_context: StoryContext
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_context)

    for stored_msg in stream_runner._messages:
        assert stored_msg.kind == MessageKind.RESPONSE
