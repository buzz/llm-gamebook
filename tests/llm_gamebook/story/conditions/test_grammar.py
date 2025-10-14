import pyparsing as pp
import pytest

from llm_gamebook.story.conditions import bool_expr_grammar as g


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
    assert make_parser(g.string_literal).parse_string(string)[0] == g.StrLiteral(exp)


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
    assert_parse_exception(make_parser(g.string_literal), string)


@pytest.mark.parametrize(
    ("string", "exp"),
    [
        ("1", 1),
        ("78", 78),
        ("666", 666),
    ],
)
def test_int_literal_good(string: str, exp: int) -> None:
    assert make_parser(g.integer_literal).parse_string(string)[0] == g.IntLiteral(exp)


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
    assert_parse_exception(make_parser(g.integer_literal), string)


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
    assert make_parser(g.float_literal).parse_string(string)[0] == g.FloatLiteral(exp)


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
    assert_parse_exception(make_parser(g.float_literal), string)


@pytest.mark.parametrize(
    ("string", "exp"),
    [
        ("true", True),
        ("false", False),
    ],
)
def test_bool_literal_good(string: str, *, exp: bool) -> None:
    assert make_parser(g.bool_literal).parse_string(string)[0] == g.BoolLiteral(exp)


@pytest.mark.parametrize(
    "string",
    [
        "True",
        "False",
    ],
)
def test_bool_literal_bad(string: str) -> None:
    assert_parse_exception(make_parser(g.bool_literal), string)


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
    assert make_parser(g.snake_case).parse_string(string)[0] == g.SnakeCase(string)


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
    assert_parse_exception(make_parser(g.snake_case), string)


# Dot path
@pytest.mark.parametrize(
    ("string", "exp_entity_id", "exp_prop_chain"),
    [
        (
            "foo_bar.id",
            g.SnakeCase("foo_bar"),
            (g.SnakeCase("id"),),
        ),
        (
            "foo_bar.current_node.id",
            g.SnakeCase("foo_bar"),
            (g.SnakeCase("current_node"), g.SnakeCase("id")),
        ),
        (
            "foo.bar.baz.quz",
            g.SnakeCase("foo"),
            (g.SnakeCase("bar"), g.SnakeCase("baz"), g.SnakeCase("quz")),
        ),
    ],
)
def test_dot_path_good(
    string: str, exp_entity_id: g.SnakeCase, exp_prop_chain: tuple[g.SnakeCase, ...]
) -> None:
    assert make_parser(g.dot_path).parse_string(string)[0] == g.DotPath(
        exp_entity_id, exp_prop_chain
    )


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
    assert_parse_exception(make_parser(g.dot_path), string)


# Comparison
@pytest.mark.parametrize(
    ("string", "exp"),
    [
        (
            "foo.bar <= 0.99",
            (
                g.DotPath(g.SnakeCase("foo"), (g.SnakeCase("bar"),)),
                g.ComparisonOperator("<="),
                g.FloatLiteral(0.99),
            ),
        ),
        (
            "6 > 3",
            (
                g.IntLiteral(6),
                g.ComparisonOperator(">"),
                g.IntLiteral(3),
            ),
        ),
        (
            "'in_the_living_room' != locations.current_node.id",
            (
                g.StrLiteral("in_the_living_room"),
                g.ComparisonOperator("!="),
                g.DotPath(
                    g.SnakeCase("locations"), (g.SnakeCase("current_node"), g.SnakeCase("id"))
                ),
            ),
        ),
        (
            "foo.bar.baz.quz.count > 67",
            (
                g.DotPath(
                    g.SnakeCase("foo"),
                    (
                        g.SnakeCase("bar"),
                        g.SnakeCase("baz"),
                        g.SnakeCase("quz"),
                        g.SnakeCase("count"),
                    ),
                ),
                g.ComparisonOperator(">"),
                g.IntLiteral(67),
            ),
        ),
        (
            "false != false",
            (
                g.BoolLiteral(value=False),
                g.ComparisonOperator("!="),
                g.BoolLiteral(value=False),
            ),
        ),
    ],
)
def test_comparison_good(string: str, exp: tuple) -> None:
    assert g.comparison.parse_string(string)[0] == g.Comparison(*exp)


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
    assert_parse_exception(g.comparison, string)


# Boolean expression grammar
@pytest.mark.parametrize(
    ("string", "exp"),
    [
        (
            "foo.bar <= 0.99 and not foo.status == 'ok'",
            g.AndExpr(
                left=g.Comparison(
                    g.DotPath(g.SnakeCase("foo"), (g.SnakeCase("bar"),)),
                    g.ComparisonOperator("<="),
                    g.FloatLiteral(0.99),
                ),
                right=g.NotExpr(
                    expr=g.Comparison(
                        g.DotPath(g.SnakeCase("foo"), (g.SnakeCase("status"),)),
                        g.ComparisonOperator("=="),
                        g.StrLiteral("ok"),
                    )
                ),
            ),
        ),
        (
            "true or false and foo.bar == 10",
            g.OrExpr(
                left=g.BoolLiteral(value=True),
                right=g.AndExpr(
                    left=g.BoolLiteral(value=False),
                    right=g.Comparison(
                        g.DotPath(g.SnakeCase("foo"), (g.SnakeCase("bar"),)),
                        g.ComparisonOperator("=="),
                        g.IntLiteral(10),
                    ),
                ),
            ),
        ),
        (
            "not foo.bar != 5 or baz.qux == 'yes'",
            g.OrExpr(
                left=g.NotExpr(
                    expr=g.Comparison(
                        g.DotPath(g.SnakeCase("foo"), (g.SnakeCase("bar"),)),
                        g.ComparisonOperator("!="),
                        g.IntLiteral(5),
                    )
                ),
                right=g.Comparison(
                    g.DotPath(g.SnakeCase("baz"), (g.SnakeCase("qux"),)),
                    g.ComparisonOperator("=="),
                    g.StrLiteral("yes"),
                ),
            ),
        ),
        (
            "foo_bar.id",
            g.DotPath(g.SnakeCase("foo_bar"), (g.SnakeCase("id"),)),
        ),
        (
            "''",
            g.StrLiteral(""),
        ),
        (
            "true",
            g.BoolLiteral(value=True),
        ),
        (
            "66",
            g.IntLiteral(66),
        ),
        (
            "1.234",
            g.FloatLiteral(1.234),
        ),
    ],
)
def test_bool_expr_good(string: str, exp: g.BoolExpr) -> None:
    assert g.bool_expr.parse_string(string)[0] == exp


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
    assert_parse_exception(g.bool_expr, string)
