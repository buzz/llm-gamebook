from uuid import uuid4

import pytest
from pydantic_ai.messages import TextPart, ThinkingPart, ToolCallPart

from llm_gamebook.web.schema.session.part import TextPart as AppTextPart
from llm_gamebook.web.schema.session.part import ThinkingPart as AppThinkingPart
from llm_gamebook.web.schema.session.part import ToolCallPart as AppToolCallPart
from llm_gamebook.web.schema.websocket._convert_part import convert_part


def test_convert_part_text() -> None:
    """Test converting pydantic_ai TextPart to API schema."""
    part_id = uuid4()
    pydantic_part = TextPart(content="Hello, world!")

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppTextPart)
    assert result.id == part_id
    assert result.content == "Hello, world!"


def test_convert_part_thinking() -> None:
    """Test converting pydantic_ai ThinkingPart to API schema."""
    part_id = uuid4()
    pydantic_part = ThinkingPart(content="Thinking process...", provider_name="openai")

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppThinkingPart)
    assert result.id == part_id
    assert result.content == "Thinking process..."
    assert result.provider_name == "openai"


def test_convert_part_thinking_without_provider() -> None:
    """Test converting ThinkingPart without provider_name."""
    part_id = uuid4()
    pydantic_part = ThinkingPart(content="Thinking process...")

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppThinkingPart)
    assert result.content == "Thinking process..."
    assert result.provider_name is None


def test_convert_part_tool_call() -> None:
    """Test converting pydantic_ai ToolCallPart to API schema."""
    part_id = uuid4()
    pydantic_part = ToolCallPart(
        tool_name="get_weather",
        args='{"location": "NYC"}',
        tool_call_id="call-123",
    )

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppToolCallPart)
    assert result.id == part_id
    assert result.tool_name == "get_weather"
    assert result.args == '{"location": "NYC"}'
    assert result.tool_call_id == "call-123"


def test_convert_part_tool_call_dict_args() -> None:
    """Test converting ToolCallPart with dict args to JSON string."""
    part_id = uuid4()
    pydantic_part = ToolCallPart(
        tool_name="get_weather",
        args={"location": "NYC", "units": "celsius"},
        tool_call_id="call-456",
    )

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppToolCallPart)
    assert result.tool_name == "get_weather"
    assert result.args == '{"location": "NYC", "units": "celsius"}'
    assert result.tool_call_id == "call-456"


def test_convert_part_tool_call_list_args() -> None:
    """Test converting ToolCallPart with list args to JSON string."""
    part_id = uuid4()
    pydantic_part = ToolCallPart(
        tool_name="search",
        args={"answer": 42},
        tool_call_id="call-789",
    )

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppToolCallPart)
    assert result.tool_name == "search"
    assert result.args == '{"answer": 42}'
    assert result.tool_call_id == "call-789"


def test_convert_part_tool_call_string_args_unchanged() -> None:
    """Test that string args are passed through unchanged."""
    part_id = uuid4()
    pydantic_part = ToolCallPart(
        tool_name="echo",
        args='{"message": "test"}',
        tool_call_id="call-000",
    )

    result = convert_part(pydantic_part, part_id)

    assert isinstance(result, AppToolCallPart)
    assert result.args == '{"message": "test"}'


def test_convert_part_unknown_type() -> None:
    """Test error handling for unknown part types."""
    part_id = uuid4()

    class UnknownPart:
        pass

    unknown_part = UnknownPart()

    with pytest.raises(TypeError, match="Unknown part type"):
        convert_part(unknown_part, part_id)
