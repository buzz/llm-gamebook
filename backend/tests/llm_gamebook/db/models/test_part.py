from datetime import UTC, datetime
from json import dumps as json_dumps

import pytest
from pydantic_ai import RetryPromptPart
from pydantic_ai.messages import (
    SystemPromptPart,
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)

from llm_gamebook.db.models import Part
from llm_gamebook.db.models.part import PartKind


def test_part_from_user_prompt() -> None:
    request_part = UserPromptPart(
        content="Hello, world!",
        timestamp=datetime.now(UTC),
    )
    part = Part.from_model_request_part(request_part)

    assert part.kind == PartKind.USER_PROMPT
    assert part.content == "Hello, world!"
    assert part.timestamp == request_part.timestamp
    assert part.tool_name is None
    assert part.tool_call_id is None
    assert part.args is None


def test_part_from_tool_return() -> None:
    request_part = ToolReturnPart(
        tool_name="get_weather",
        tool_call_id="call-123",
        content="The weather is sunny",
    )
    part = Part.from_model_request_part(request_part)

    assert part.kind == PartKind.TOOL_RETURN
    assert part.content == "The weather is sunny"
    assert part.tool_name == "get_weather"
    assert part.tool_call_id == "call-123"
    assert part.args is None


def test_part_from_tool_return_dict_content() -> None:
    request_part = ToolReturnPart(
        tool_name="get_weather",
        tool_call_id="call-123",
        content={"temperature": 72, "city": "NYC"},
    )
    part = Part.from_model_request_part(request_part)

    assert part.kind == PartKind.TOOL_RETURN
    assert part.content == '{"temperature": 72, "city": "NYC"}'
    assert part.tool_name == "get_weather"
    assert part.tool_call_id == "call-123"


def test_part_from_tool_return_list_content() -> None:
    request_part = ToolReturnPart(
        tool_name="get_items",
        tool_call_id="call-456",
        content=["item1", "item2"],
    )
    part = Part.from_model_request_part(request_part)

    assert part.kind == PartKind.TOOL_RETURN
    assert part.content == '["item1", "item2"]'
    assert part.tool_name == "get_items"
    assert part.tool_call_id == "call-456"


def test_part_from_retry_prompt() -> None:
    request_part = RetryPromptPart(
        tool_name="search",
        tool_call_id="retry-123",
        content="Please try again",
    )
    part = Part.from_model_request_part(request_part)

    assert part.kind == PartKind.RETRY_PROMPT
    assert part.content == "Please try again"
    assert part.tool_name == "search"
    assert part.tool_call_id == "retry-123"


def test_part_from_text() -> None:
    response_part = TextPart(content="Hello, world!")
    part = Part.from_model_response_part(response_part)

    assert part.kind == PartKind.TEXT
    assert part.content == "Hello, world!"
    assert part.tool_name is None
    assert part.tool_call_id is None
    assert part.args is None


def test_part_from_thinking() -> None:
    response_part = ThinkingPart(content="Thinking process...")
    part = Part.from_model_response_part(response_part)

    assert part.kind == PartKind.THINKING
    assert part.content == "Thinking process..."
    assert part.tool_name is None
    assert part.tool_call_id is None
    assert part.args is None


def test_part_from_tool_call() -> None:
    response_part = ToolCallPart(
        tool_name="get_weather",
        args='{"location": "NYC"}',
        tool_call_id="call-123",
    )
    part = Part.from_model_response_part(response_part)

    assert part.kind == PartKind.TOOL_CALL
    assert part.tool_name == "get_weather"
    assert part.args == '{"location": "NYC"}'
    assert part.tool_call_id == "call-123"
    assert part.content is None


def test_part_from_tool_call_args_dict() -> None:
    response_part = ToolCallPart(
        tool_name="get_weather",
        args={"location": "NYC", "units": "imperial"},
        tool_call_id="call-456",
    )
    part = Part.from_model_response_part(response_part)

    assert part.kind == PartKind.TOOL_CALL
    assert part.tool_name == "get_weather"
    assert part.args == '{"location": "NYC", "units": "imperial"}'
    assert part.tool_call_id == "call-456"


def test_part_from_tool_call_args_list() -> None:
    response_part = ToolCallPart(
        tool_name="get_items",
        args=json_dumps(["a", "b", "c"]),
        tool_call_id="call-789",
    )
    part = Part.from_model_response_part(response_part)

    assert part.kind == PartKind.TOOL_CALL
    assert part.tool_name == "get_items"
    assert part.args == '["a", "b", "c"]'
    assert part.tool_call_id == "call-789"


def test_part_unsupported_request_type() -> None:
    request_part = SystemPromptPart(content="System message")

    with pytest.raises(TypeError, match="Unsupported part type"):
        Part.from_model_request_part(request_part)


def test_part_unsupported_response_type() -> None:
    class UnsupportedResponsePart:
        part_kind = "unknown"

    response_part = UnsupportedResponsePart()

    with pytest.raises(TypeError, match="Unsupported part type"):
        Part.from_model_response_part(response_part)  # type: ignore[arg-type]


def test_part_to_model_request_part() -> None:
    part = Part(
        kind=PartKind.USER_PROMPT,
        content="Foo",
        tool_call_id=None,
        tool_name=None,
        args=None,
    )
    model_part = part.to_model_request_part()

    assert model_part.part_kind == "user-prompt"
    assert model_part.content == "Foo"


def test_part_to_model_response_part() -> None:
    part = Part(
        kind=PartKind.TEXT,
        content="Bar",
        tool_call_id=None,
        tool_name=None,
        args=None,
    )
    model_part = part.to_model_response_part()

    assert model_part.part_kind == "text"
    assert model_part.content == "Bar"


def test_part_to_model_request_part_fails_with_wrong_type() -> None:
    part = Part(
        kind=PartKind.TEXT,
        content="Bar",
        tool_call_id=None,
        tool_name=None,
        args=None,
    )

    with pytest.raises(ValueError, match="Expected kind"):
        part.to_model_request_part()


def test_part_to_model_response_part_fails_with_wrong_type() -> None:
    part = Part(
        kind=PartKind.USER_PROMPT,
        content="Bar",
        tool_call_id=None,
        tool_name=None,
        args=None,
    )

    with pytest.raises(ValueError, match="Expected kind"):
        part.to_model_response_part()
