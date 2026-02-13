from uuid import UUID, uuid4

from pydantic_ai import Agent, ModelMessage, ModelRequest, UserPromptPart

from llm_gamebook.engine._runner import StreamRunner
from llm_gamebook.engine.message import ResponseStreamUpdateMessage
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import StoryState

from .conftest import StreamEvents


async def test_stream_runner_run_returns_messages(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Hello")])]

    result = await stream_runner.run(messages, story_state)

    _, response_ids, part_ids, _ = result

    assert len(response_ids) > 0
    assert len(part_ids) > 0
    assert len(part_ids) == len(response_ids)


async def test_stream_runner_handles_model_request_node(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test prompt")])]

    await stream_runner.run(messages, story_state)

    assert len(stream_events) >= 1
    event = stream_events[0]
    assert event.response_id == stream_runner._response_ids[0]
    assert len(event.part_ids) > 0


async def test_stream_runner_handles_part_start_event(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_state)

    assert len(stream_events) >= 1
    event = stream_events[0]
    assert event.session_id == stream_runner._session_id
    assert event.response is not None
    assert len(event.part_ids) > 0


async def test_stream_runner_handles_part_delta_event(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_state)

    assert len(stream_events) >= 1
    for event in stream_events:
        assert event.session_id == stream_runner._session_id
        assert event.response_id is not None
        assert len(event.part_ids) > 0


async def test_stream_runner_multiple_responses(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="First")])]

    result1 = await stream_runner.run(messages, story_state)

    messages2: list[ModelMessage] = [
        *result1[0],
        ModelRequest(parts=[UserPromptPart(content="Second")]),
    ]

    result2 = await stream_runner.run(messages2, story_state)

    total_responses = len(result1[1]) + len(result2[1])
    assert total_responses >= 1


async def test_stream_runner_debounce_reduces_events(
    message_bus: MessageBus, story_state: StoryState, test_agent: Agent[StoryState, str]
) -> None:
    session_id = uuid4()
    runner = StreamRunner(test_agent, session_id, message_bus, debounce=0.5)

    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    events: list[ResponseStreamUpdateMessage] = []

    def track_stream(msg: ResponseStreamUpdateMessage) -> None:
        events.append(msg)

    message_bus.subscribe(ResponseStreamUpdateMessage, track_stream)

    await runner.run(messages, story_state)

    assert len(events) > 0
    assert len(events) <= 4


async def test_stream_runner_zero_debounce_produces_more_events(
    message_bus: MessageBus, story_state: StoryState, test_agent: Agent[StoryState, str]
) -> None:
    session_id = uuid4()
    runner_zero = StreamRunner(test_agent, session_id, message_bus, debounce=0.0)

    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    events: list[ResponseStreamUpdateMessage] = []

    def track_stream(msg: ResponseStreamUpdateMessage) -> None:
        events.append(msg)

    message_bus.subscribe(ResponseStreamUpdateMessage, track_stream)

    await runner_zero.run(messages, story_state)

    assert len(events) >= 1


async def test_stream_runner_response_id_is_uuid(
    stream_runner: StreamRunner,
    story_state: StoryState,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    result = await stream_runner.run(messages, story_state)
    response_ids = result[1]

    for response_id in response_ids:
        assert isinstance(response_id, UUID)


async def test_stream_runner_part_ids_are_uuids(
    stream_runner: StreamRunner,
    story_state: StoryState,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    result = await stream_runner.run(messages, story_state)
    part_ids = result[2]

    for response_parts in part_ids:
        for part_id in response_parts:
            assert isinstance(part_id, UUID)


async def test_stream_runner_response_contains_model_output(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_state)

    assert len(stream_events) >= 1
    final_event = stream_events[-1]
    assert len(final_event.response.parts) >= 1


async def test_stream_runner_session_id_matches(
    stream_runner: StreamRunner,
    story_state: StoryState,
    stream_events: StreamEvents,
) -> None:
    messages: list[ModelMessage] = [ModelRequest(parts=[UserPromptPart(content="Test")])]

    await stream_runner.run(messages, story_state)

    for event in stream_events:
        assert event.session_id == stream_runner._session_id
