import pytest

from llm_gamebook.schema.validators import (
    id_from_name,
    is_normalized_pascal_case,
    is_normalized_snake_case,
)


def test_is_normalized_snake_case_valid() -> None:
    """Test validating valid snake_case strings."""
    assert is_normalized_snake_case("my_variable") == "my_variable"
    assert is_normalized_snake_case("hello_world") == "hello_world"
    assert is_normalized_snake_case("a_b_c") == "a_b_c"
    assert is_normalized_snake_case("test") == "test"


def test_is_normalized_snake_case_invalid() -> None:
    """Test that invalid snake_case raises ValueError."""
    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        is_normalized_snake_case("MyVariable")
    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        is_normalized_snake_case("my-variable")
    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        is_normalized_snake_case("my variable")
    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        is_normalized_snake_case("my__variable")


def test_is_normalized_pascal_case_valid() -> None:
    """Test validating valid PascalCase strings."""
    assert is_normalized_pascal_case("MyVariable") == "MyVariable"
    assert is_normalized_pascal_case("HelloWorld") == "HelloWorld"
    assert is_normalized_pascal_case("Abc") == "Abc"
    assert is_normalized_pascal_case("Test") == "Test"


def test_is_normalized_pascal_case_invalid() -> None:
    """Test that invalid PascalCase raises ValueError."""
    with pytest.raises(ValueError, match="Invalid normalized PascalCase format"):
        is_normalized_pascal_case("my_variable")
    with pytest.raises(ValueError, match="Invalid normalized PascalCase format"):
        is_normalized_pascal_case("my-variable")
    with pytest.raises(ValueError, match="Invalid normalized PascalCase format"):
        is_normalized_pascal_case("my variable")
    with pytest.raises(ValueError, match="Invalid normalized PascalCase format"):
        is_normalized_pascal_case("myVar")


def _generate_id(name: str) -> str:
    return f"id_{name.lower().replace(' ', '_')}"


def test_id_from_name_with_name() -> None:
    """Test auto-generating ID from name field."""
    data = {"name": "Test Entity"}
    result = id_from_name(data, _generate_id)

    assert isinstance(result, dict)
    assert result["id"] == "id_test_entity"
    assert result["name"] == "Test Entity"


def test_id_from_name_without_name() -> None:
    """Test leaving data unchanged when name field is missing."""
    data = {"other_field": "value"}
    result = id_from_name(data, _generate_id)

    assert isinstance(result, dict)
    assert "id" not in result
    assert result["other_field"] == "value"


def test_id_from_name_with_existing_id() -> None:
    """Test leaving existing ID unchanged."""
    data = {"name": "Test", "id": "existing_id"}
    result = id_from_name(data, _generate_id)

    assert isinstance(result, dict)
    assert result["id"] == "existing_id"
