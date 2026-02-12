import pytest


@pytest.mark.skip(reason="Not yet implemented")
def test_convert_part_text() -> None:
    """Test converting pydantic_ai TextPart to API schema."""


@pytest.mark.skip(reason="Not yet implemented")
def test_convert_part_thinking() -> None:
    """Test converting pydantic_ai ThinkingPart to API schema."""


@pytest.mark.skip(reason="Not yet implemented")
def test_convert_part_tool_call() -> None:
    """Test converting pydantic_ai ToolCallPart to API schema."""


@pytest.mark.skip(reason="Not yet implemented")
def test_convert_part_tool_call_dict_args() -> None:
    """Test converting ToolCallPart with dict args to JSON string."""


@pytest.mark.skip(reason="Not yet implemented")
def test_convert_part_tool_call_list_args() -> None:
    """Test converting ToolCallPart with list args to JSON string."""


@pytest.mark.skip(reason="Not yet implemented")
def test_convert_part_unknown_type() -> None:
    """Test error handling for unknown part types."""
