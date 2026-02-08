from uuid import uuid4

from pydantic_ai.messages import (
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
)

from llm_gamebook.db.models.part import Part, PartKind


def test_part_from_model_parts_text() -> None:
    parts = [TextPart(content="Hello, world!")]
    result = list(Part.from_model_parts(parts))

    assert len(result) == 1
    part = result[0]
    assert part.part_kind == PartKind.TEXT
    assert part.content == "Hello, world!"
    assert part.timestamp is None
    assert part.tool_name is None
    assert part.tool_call_id is None
    assert part.args is None
    assert part.duration_seconds is None


def test_part_from_model_parts_thinking() -> None:
    parts = [ThinkingPart(content="Thinking process...")]
    result = list(Part.from_model_parts(parts))

    assert len(result) == 1
    part = result[0]
    assert part.part_kind == PartKind.THINKING
    assert part.content == "Thinking process..."


def test_part_from_model_parts_tool_call() -> None:
    parts = [
        ToolCallPart(
            tool_name="get_weather",
            args='{"location": "NYC"}',
            tool_call_id="call-123",
        )
    ]
    result = list(Part.from_model_parts(parts))

    assert len(result) == 1
    part = result[0]
    assert part.part_kind == PartKind.TOOL_CALL
    assert part.tool_name == "get_weather"
    assert part.args == '{"location": "NYC"}'
    assert part.tool_call_id == "call-123"


def test_part_from_model_parts_tool_return_dict() -> None:
    parts = [
        ToolReturnPart(
            tool_name="get_weather",
            content={"temperature": 72, "city": "NYC"},
            tool_call_id="call-123",
        )
    ]
    result = list(Part.from_model_parts(parts))

    assert len(result) == 1
    part = result[0]
    assert part.part_kind == PartKind.TOOL_RETURN
    assert part.content == '{"temperature": 72, "city": "NYC"}'


def test_part_from_model_parts_tool_return_string() -> None:
    parts = [
        ToolReturnPart(
            tool_name="get_weather",
            content="The weather is sunny",
            tool_call_id="call-456",
        )
    ]
    result = list(Part.from_model_parts(parts))

    assert len(result) == 1
    part = result[0]
    assert part.part_kind == PartKind.TOOL_RETURN
    assert part.content == "The weather is sunny"


def test_part_from_model_parts_with_part_ids() -> None:
    parts = [TextPart(content="Test")]
    custom_id = uuid4()
    part_ids = [custom_id]

    result = list(Part.from_model_parts(parts, part_ids=part_ids))

    assert len(result) == 1
    assert result[0].id == custom_id


def test_part_from_model_parts_with_durations() -> None:
    parts = [ThinkingPart(content="Thinking...")]
    custom_id = uuid4()
    part_ids = [custom_id]
    durations = {custom_id: 42}

    result = list(Part.from_model_parts(parts, part_ids=part_ids, durations=durations))

    assert len(result) == 1
    assert result[0].duration_seconds == 42
