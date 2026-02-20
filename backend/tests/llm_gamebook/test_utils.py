import pytest

from llm_gamebook.utils import (
    normalize,
    normalized_kebab_case,
    normalized_pascal_case,
    normalized_snake_case,
)


@pytest.mark.parametrize("value", ["hello world", "Hello World", "test_123"])
def test_normalize_ascii(value: str) -> None:
    """Test normalizing ASCII text."""
    assert normalize(value) == value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("café", "cafe"),
        ("naïve", "naive"),
        ("résumé", "resume"),
        ("Héllo Wörld", "Hello World"),
        ("日本語", ""),
    ],
)
def test_normalize_unicode(value: str, expected: str) -> None:
    """Test normalizing unicode characters (removes accents)."""
    assert normalize(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello world", "hello_world"),
        ("Hello World", "hello_world"),
        ("test 123", "test_123"),
        ("fooBarBaz", "foo_bar_baz"),
        ("café coffee", "cafe_coffee"),
        ("Héllo Wörld", "hello_world"),
        ("naïve approach", "naive_approach"),
    ],
)
def test_normalized_snake_case(value: str, expected: str) -> None:
    """Test converting simple text to snake_case."""
    assert normalized_snake_case(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello world", "HelloWorld"),
        ("Hello World", "HelloWorld"),
        ("test 123", "Test123"),
        ("foo_bar", "FooBar"),
        ("café coffee", "CafeCoffee"),
        ("Héllo Wörld", "HelloWorld"),
        ("naïve approach", "NaiveApproach"),
    ],
)
def test_normalized_pascal_case(value: str, expected: str) -> None:
    """Test converting simple text to PascalCase."""
    assert normalized_pascal_case(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello world", "hello-world"),
        ("Hello World", "hello-world"),
        ("test 123", "test-123"),
        ("foo_bar", "foo-bar"),
        ("café coffee", "cafe-coffee"),
        ("Héllo Wörld", "hello-world"),
        ("naïve approach", "naive-approach"),
    ],
)
def test_normalized_kebab_case(value: str, expected: str) -> None:
    assert normalized_kebab_case(value) == expected
