import pyparsing as pp
import pytest

from llm_gamebook.story.conditions.expression import (
    AndExpr,
    BoolExpr,
    BoolLiteral,
    Comparison,
    ComparisonOperator,
    DotPath,
    FloatLiteral,
    IntLiteral,
    NotExpr,
    OrExpr,
    SnakeCase,
    StrLiteral,
    bool_expr,
    bool_literal,
    comparison,
    dot_path,
    float_literal,
    integer_literal,
    snake_case,
    string_literal,
)


def make_parser(el: pp.ParserElement) -> pp.ParserElement:
    return (pp.StringStart() + el + pp.StringEnd()).leave_whitespace()


def assert_parse_exception(el: pp.ParserElement, string: str) -> None:
    try:
        result = el.parse_string(string)
    except pp.ParseException:
        pass
    else:
        pytest.fail(f"{string} should raise but parsed to: {result}")


# Literals
@pytest.mark.parametrize(
    ("string", "exp"),
    [
        ("''", ""),
        ('""', ""),
        ("'foo'", "foo"),
        ('"foo"', "foo"),
        ("' foo'", " foo"),
        ('"foo "', "foo "),
        ("'in_the_living_room'", "in_the_living_room"),
    ],
)
def test_str_literal_good(string: str, exp: str) -> None:
    assert make_parser(string_literal).parse_string(string)[0] == StrLiteral(exp)


@pytest.mark.parametrize(
    "string",
    [
        " 0",
        "1 ",
        " 65 ",
        "foo",
        "1_0",
        "1.5",
        " ''",
        ' ""',
        " 'foo'",
        ' "foo"',
        "'' ",
        '"" ',
        "'foo' ",
        '"foo" ',
        " '' ",
        ' "" ',
        " 'foo' ",
        ' "foo" ',
    ],
)
def test_str_literal_bad(string: str) -> None:
    assert_parse_exception(make_parser(string_literal), string)


@pytest.mark.parametrize(
    ("string", "exp"),
    [
        ("1", 1),
        ("78", 78),
        ("666", 666),
    ],
)
def test_int_literal_good(string: str, exp: int) -> None:
    assert make_parser(integer_literal).parse_string(string)[0] == IntLiteral(exp)


@pytest.mark.parametrize(
    "string",
    [
        " 0",
        "1 ",
        " 65 ",
        "foo",
        "1_0",
        "1.5",
    ],
)
def test_int_literal_bad(string: str) -> None:
    assert_parse_exception(make_parser(integer_literal), string)


@pytest.mark.parametrize(
    ("string", "exp"),
    [
        ("0.99", 0.99),
        ("1.1", 1.1),
        ("78.999", 78.999),
        ("666.768", 666.768),
    ],
)
def test_float_literal_good(string: str, exp: float) -> None:
    assert make_parser(float_literal).parse_string(string)[0] == FloatLiteral(exp)


@pytest.mark.parametrize(
    "string",
    [
        " 0",
        "1 ",
        " 65 ",
        "foo",
        "1_0",
        "15",
        "1 .5",
        "1. 5",
        "1.5 ",
        " 1.5",
    ],
)
def test_float_literal_bad(string: str) -> None:
    assert_parse_exception(make_parser(float_literal), string)


@pytest.mark.parametrize(
    ("string", "exp"),
    [
        ("true", True),
        ("false", False),
    ],
)
def test_bool_literal_good(string: str, *, exp: bool) -> None:
    assert make_parser(bool_literal).parse_string(string)[0] == BoolLiteral(exp)


@pytest.mark.parametrize(
    "string",
    [
        "True",
        "False",
    ],
)
def test_bool_literal_bad(string: str) -> None:
    assert_parse_exception(make_parser(bool_literal), string)


# snake_case
@pytest.mark.parametrize(
    "string",
    [
        "f",
        "f_b",
        "f_b_b",
        "foo_bar",
        "foo",
        "foo_bar_baz",
    ],
)
def test_snake_case_good(string: str) -> None:
    assert make_parser(snake_case).parse_string(string)[0] == SnakeCase(string)


@pytest.mark.parametrize(
    "string",
    [
        "foo_Bar",
        "Foo_bar",
        "foo bar",
        " foo_bar",
        "foo_bar ",
        "_foo",
        "foo_",
        "_foo_bar",
        "foo_bar_",
        "_foo_bar_",
        "foo__bar",
        "foo_ bar",
        "foo _bar",
        "foo_bär",
        "f__b",
        "?",
        "f_$",
        "9",
        "1foo",
        "5aaa_bbb",
    ],
)
def test_snake_case_bad(string: str) -> None:
    assert_parse_exception(make_parser(snake_case), string)


# Dot path
@pytest.mark.parametrize(
    ("string", "exp_entity_id", "exp_prop_chain"),
    [
        (
            "foo_bar.id",
            SnakeCase("foo_bar"),
            (SnakeCase("id"),),
        ),
        (
            "foo_bar.current_node.id",
            SnakeCase("foo_bar"),
            (SnakeCase("current_node"), SnakeCase("id")),
        ),
        (
            "foo.bar.baz.quz",
            SnakeCase("foo"),
            (SnakeCase("bar"), SnakeCase("baz"), SnakeCase("quz")),
        ),
    ],
)
def test_dot_path_good(
    string: str, exp_entity_id: SnakeCase, exp_prop_chain: tuple[SnakeCase, ...]
) -> None:
    assert make_parser(dot_path).parse_string(string)[0] == DotPath(exp_entity_id, exp_prop_chain)


@pytest.mark.parametrize(
    "string",
    [
        ".",
        "_",
        " foo_bar.id",
        "foo_bar .current_node.id",
        "foo.bar.baz.quz ",
        "Foo.bar",
        "foo.Bar",
        "foo bar",
        "foo",
        "_foo",
        "foo._bar",
    ],
)
def test_dot_path_bad(string: str) -> None:
    assert_parse_exception(make_parser(dot_path), string)


# Comparison
@pytest.mark.parametrize(
    ("string", "exp"),
    [
        (
            "foo.bar <= 0.99",
            (
                DotPath(SnakeCase("foo"), (SnakeCase("bar"),)),
                ComparisonOperator("<="),
                FloatLiteral(0.99),
            ),
        ),
        (
            "6 > 3",
            (
                IntLiteral(6),
                ComparisonOperator(">"),
                IntLiteral(3),
            ),
        ),
        (
            "'in_the_living_room' != locations.current_node.id",
            (
                StrLiteral("in_the_living_room"),
                ComparisonOperator("!="),
                DotPath(SnakeCase("locations"), (SnakeCase("current_node"), SnakeCase("id"))),
            ),
        ),
        (
            "foo.bar.baz.quz.count > 67",
            (
                DotPath(
                    SnakeCase("foo"),
                    (SnakeCase("bar"), SnakeCase("baz"), SnakeCase("quz"), SnakeCase("count")),
                ),
                ComparisonOperator(">"),
                IntLiteral(67),
            ),
        ),
        (
            "false != false",
            (
                BoolLiteral(value=False),
                ComparisonOperator("!="),
                BoolLiteral(value=False),
            ),
        ),
    ],
)
def test_comparison_good(string: str, exp: tuple) -> None:
    assert comparison.parse_string(string)[0] == Comparison(*exp)


@pytest.mark.parametrize(
    "string",
    [
        ".",
        "_",
        " foo_bar.id",
        "foo_bar .current_node.id",
        "foo.bar.baz.quz ",
        "Foo.bar",
        "foo.Bar",
        "foo bar",
        "foo",
        "_foo",
        "foo._bar",
        "false ! = false",
        "foo.bar.baz.quz.count > #",
        "foo ! bar",
        "6 = 6",
        "66",
        "1.234",
    ],
)
def test_comparison_bad(string: str) -> None:
    assert_parse_exception(comparison, string)


# Boolean expression grammar
@pytest.mark.parametrize(
    ("string", "exp"),
    [
        (
            "foo.bar <= 0.99 and not foo.status == 'ok'",
            AndExpr(
                left=Comparison(
                    DotPath(SnakeCase("foo"), (SnakeCase("bar"),)),
                    ComparisonOperator("<="),
                    FloatLiteral(0.99),
                ),
                right=NotExpr(
                    expr=Comparison(
                        DotPath(SnakeCase("foo"), (SnakeCase("status"),)),
                        ComparisonOperator("=="),
                        StrLiteral("ok"),
                    )
                ),
            ),
        ),
        (
            "true or false and foo.bar == 10",
            OrExpr(
                left=BoolLiteral(value=True),
                right=AndExpr(
                    left=BoolLiteral(value=False),
                    right=Comparison(
                        DotPath(SnakeCase("foo"), (SnakeCase("bar"),)),
                        ComparisonOperator("=="),
                        IntLiteral(10),
                    ),
                ),
            ),
        ),
        (
            "not foo.bar != 5 or baz.qux == 'yes'",
            OrExpr(
                left=NotExpr(
                    expr=Comparison(
                        DotPath(SnakeCase("foo"), (SnakeCase("bar"),)),
                        ComparisonOperator("!="),
                        IntLiteral(5),
                    )
                ),
                right=Comparison(
                    DotPath(SnakeCase("baz"), (SnakeCase("qux"),)),
                    ComparisonOperator("=="),
                    StrLiteral("yes"),
                ),
            ),
        ),
        (
            "foo_bar.id",
            DotPath(SnakeCase("foo_bar"), (SnakeCase("id"),)),
        ),
        (
            "''",
            StrLiteral(""),
        ),
        (
            "true",
            BoolLiteral(value=True),
        ),
        (
            "66",
            IntLiteral(66),
        ),
        (
            "1.234",
            FloatLiteral(1.234),
        ),
    ],
)
def test_bool_expr_good(string: str, exp: BoolExpr) -> None:
    assert bool_expr.parse_string(string)[0] == exp


@pytest.mark.parametrize(
    "string",
    [
        ".",
        "_",
        "foo_bar .current_node.id",
        "foo.bar.baz.quz ",
        "Foo.bar",
        "foo.Bar",
        "foo bar",
        "foo",
        "_foo",
        "foo._bar",
        "false ! = false",
        "foo.bar.baz.quz.count > 6 7",
        "foo ! bar",
        "6 = 6",
    ],
)
def test_bool_expr_bad(string: str) -> None:
    assert_parse_exception(bool_expr, string)
