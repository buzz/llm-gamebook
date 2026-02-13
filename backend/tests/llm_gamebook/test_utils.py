from llm_gamebook.utils import normalize, normalized_pascal_case, normalized_snake_case


def test_normalize_ascii() -> None:
    """Test normalizing ASCII text."""
    assert normalize("hello world") == "hello world"
    assert normalize("Hello World") == "Hello World"
    assert normalize("test_123") == "test_123"


def test_normalize_unicode() -> None:
    """Test normalizing unicode characters (removes accents)."""
    assert normalize("café") == "cafe"
    assert normalize("naïve") == "naive"
    assert normalize("résumé") == "resume"
    assert normalize("Héllo Wörld") == "Hello World"
    assert not normalize("日本語")


def test_normalized_snake_case_simple() -> None:
    """Test converting simple text to snake_case."""
    assert normalized_snake_case("hello world") == "hello_world"
    assert normalized_snake_case("Hello World") == "hello_world"
    assert normalized_snake_case("test 123") == "test_123"
    assert normalized_snake_case("fooBarBaz") == "foo_bar_baz"


def test_normalized_snake_case_with_unicode() -> None:
    """Test converting text with unicode to snake_case."""
    assert normalized_snake_case("café coffee") == "cafe_coffee"
    assert normalized_snake_case("Héllo Wörld") == "hello_world"
    assert normalized_snake_case("naïve approach") == "naive_approach"


def test_normalized_pascal_case_simple() -> None:
    """Test converting simple text to PascalCase."""
    assert normalized_pascal_case("hello world") == "HelloWorld"
    assert normalized_pascal_case("Hello World") == "HelloWorld"
    assert normalized_pascal_case("test 123") == "Test123"
    assert normalized_pascal_case("foo_bar") == "FooBar"


def test_normalized_pascal_case_with_unicode() -> None:
    """Test converting text with unicode to PascalCase."""
    assert normalized_pascal_case("café coffee") == "CafeCoffee"
    assert normalized_pascal_case("Héllo Wörld") == "HelloWorld"
    assert normalized_pascal_case("naïve approach") == "NaiveApproach"
