import pytest

from llm_gamebook.story.schemas.validators import (
    is_normalized_kebab_case,
    is_normalized_pascal_case,
    is_normalized_snake_case,
    is_valid_project_id,
)


@pytest.mark.parametrize("value", ["my-variable", "hello-world", "a-b-c", "test"])
def test_is_normalized_kebab_case_valid(value: str) -> None:
    assert is_normalized_kebab_case(value) == value


@pytest.mark.parametrize("value", ["MyVariable", "my_variable", "my variable", "my--variable", ""])
def test_is_normalized_kebab_case_invalid(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid normalized kebab-case format"):
        is_normalized_kebab_case(value)


@pytest.mark.parametrize("value", ["my_variable", "hello_world", "a_b_c", "test"])
def test_is_normalized_snake_case_valid(value: str) -> None:
    assert is_normalized_snake_case(value) == value


@pytest.mark.parametrize("value", ["MyVariable", "my-variable", "my variable", "my__variable", ""])
def test_is_normalized_snake_case_invalid(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        is_normalized_snake_case(value)


@pytest.mark.parametrize("value", ["MyVariable", "HelloWorld", "Abc", "Test"])
def test_is_normalized_pascal_case_valid(value: str) -> None:
    assert is_normalized_pascal_case(value) == value


@pytest.mark.parametrize("value", ["my_variable", "my-variable", "my variable", "myVar", ""])
def test_is_normalized_pascal_case_invalid(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid normalized PascalCase format"):
        is_normalized_pascal_case(value)


@pytest.mark.parametrize(
    "value",
    [
        "foo/bar",
        "my/proj",
        "foo-bar/baz",
        "foo-bar/baz-quz",
        "foo/baz-quz",
    ],
)
def test_is_valid_project_id_valid(value: str) -> None:
    assert is_valid_project_id(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "project",
        "my-project",
        r"my\project",
        "myProj",
    ],
)
def test_is_valid_project_id_invalid_parts(value: str) -> None:
    with pytest.raises(ValueError, match="not enough values to unpack"):
        is_valid_project_id(value)


@pytest.mark.parametrize(
    "value",
    [
        "foo/bar/baz",
        "/bar",
        "foo/",
        "foo//bar",
        "Foo/bar",
    ],
)
def test_is_valid_project_id_invalid(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid normalized kebab-case format"):
        is_valid_project_id(value)
