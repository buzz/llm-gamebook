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
        pytest.fail(f"'{string}' should raise but parsed to: {result}")


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
        ("'living_room'", "living_room"),
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


type ExpType = tuple[g.Literal | g.DotPath, g.ComparisonOperator, g.Literal | g.DotPath]


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
            "'living_room' != locations.current_node.id",
            (
                g.StrLiteral("living_room"),
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
def test_comparison_good(string: str, exp: ExpType) -> None:
    left, op, right = exp
    assert g.comparison.parse_string(string)[0] == g.Comparison(left, op, right)


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
            "node_a.enabled or node_b.enabled",
            g.OrExpr(
                left=g.DotPath(
                    entity_id=g.SnakeCase(value="node_a"),
                    property_chain=(g.SnakeCase(value="enabled"),),
                ),
                right=g.DotPath(
                    entity_id=g.SnakeCase(value="node_b"),
                    property_chain=(g.SnakeCase(value="enabled"),),
                ),
            ),
        ),
        # 1. Operator Precedence: 'and' should bind tighter than 'or'
        (
            "a.x or b.y and c.z",
            g.OrExpr(
                left=g.DotPath(g.SnakeCase("a"), (g.SnakeCase("x"),)),
                right=g.AndExpr(
                    left=g.DotPath(g.SnakeCase("b"), (g.SnakeCase("y"),)),
                    right=g.DotPath(g.SnakeCase("c"), (g.SnakeCase("z"),)),
                ),
            ),
        ),
        # 2. Parentheses: Overriding default precedence
        (
            "(a.x or b.y) and c.z",
            g.AndExpr(
                left=g.OrExpr(
                    left=g.DotPath(g.SnakeCase("a"), (g.SnakeCase("x"),)),
                    right=g.DotPath(g.SnakeCase("b"), (g.SnakeCase("y"),)),
                ),
                right=g.DotPath(g.SnakeCase("c"), (g.SnakeCase("z"),)),
            ),
        ),
        # 3. Chained AND (Left Associativity): (A and B) and C
        (
            "node.a and node.b and node.c",
            g.AndExpr(
                left=g.AndExpr(
                    left=g.DotPath(g.SnakeCase("node"), (g.SnakeCase("a"),)),
                    right=g.DotPath(g.SnakeCase("node"), (g.SnakeCase("b"),)),
                ),
                right=g.DotPath(g.SnakeCase("node"), (g.SnakeCase("c"),)),
            ),
        ),
        # 4. Double NOT (Right Associativity): not (not A)
        (
            "not not node.active",
            g.NotExpr(
                expr=g.NotExpr(expr=g.DotPath(g.SnakeCase("node"), (g.SnakeCase("active"),)))
            ),
        ),
        # 5. Complex mix with literals and comparisons
        (
            "user.age > 18 or (user.vip == true and not user.banned)",
            g.OrExpr(
                left=g.Comparison(
                    g.DotPath(g.SnakeCase("user"), (g.SnakeCase("age"),)),
                    g.ComparisonOperator(">"),
                    g.IntLiteral(18),
                ),
                right=g.AndExpr(
                    left=g.Comparison(
                        g.DotPath(g.SnakeCase("user"), (g.SnakeCase("vip"),)),
                        g.ComparisonOperator("=="),
                        g.BoolLiteral(value=True),
                    ),
                    right=g.NotExpr(expr=g.DotPath(g.SnakeCase("user"), (g.SnakeCase("banned"),))),
                ),
            ),
        ),
        # 6. Deeply nested DotPath (Edge Case)
        (
            "system.sub.node.value == 10",
            g.Comparison(
                left=g.DotPath(
                    g.SnakeCase("system"),
                    (g.SnakeCase("sub"), g.SnakeCase("node"), g.SnakeCase("value")),
                ),
                op=g.ComparisonOperator("=="),
                right=g.IntLiteral(10),
            ),
        ),
        # 7. Comparison with String Literal (Edge Case)
        (
            "foo.status == 'active' or bar.status == 'pending'",
            g.OrExpr(
                left=g.Comparison(
                    g.DotPath(g.SnakeCase("foo"), (g.SnakeCase("status"),)),
                    g.ComparisonOperator("=="),
                    g.StrLiteral("active"),
                ),
                right=g.Comparison(
                    g.DotPath(g.SnakeCase("bar"), (g.SnakeCase("status"),)),
                    g.ComparisonOperator("=="),
                    g.StrLiteral("pending"),
                ),
            ),
        ),
    ],
)
def test_bool_expr_good(string: str, exp: g.BoolExpr) -> None:
    assert g.bool_expr.parse_string(string)[0] == exp


def test_bool_expr_and_or_do_not_equal() -> None:
    op = g.DotPath(g.SnakeCase(value="node_a"), (g.SnakeCase(value="enabled"),))
    a = g.AndExpr(left=op, right=op)
    b = g.OrExpr(left=op, right=op)

    # Defining `AndExpr`/`OrExpr` as tuples would silently pass equal test
    assert a != b  # type: ignore[comparison-overlap]


@pytest.mark.parametrize(
    "string",
    [
        ".",
        "_",
        "foo.bar.baz.quz ",
        "foo_bar .current_node.id",
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
    assert_parse_exception(make_parser(g.bool_expr), string)


# Edge cases for robustness
@pytest.mark.parametrize(
    "string",
    [
        # Keywords as parts of identifiers
        "standard.item == 1",
        "notary.active == true",
        "player.born_at == '1990'",
        # Complex precedence
        "a.b == 1 or c.d == 2 and e.f == 3",
        "not a.b == 1 and c.d == 2",
        # Variables on both sides
        "player.health > enemy.attack",
        # Adjacent operators (no whitespace around comparison)
        "a.b==1",
        "a.b != 1",
        "a.b < 1",
        "a.b <= 1",
        "a.b > 1",
        "a.b >= 1",
        # Deep parentheses
        "((((a.b == 1))))",
        # Nested expressions with parentheses
        "(a.b == 1 and c.d == 2) or e.f == 3",
        "(a.b == 1) or (c.d == 2)",
        # Type combinations
        "1 == 1.0",
        "'hello' in 'world'",
        "true != false",
        # Unary operator stacking
        "not not a.b == 1",
    ],
)
def test_bool_expr_edge_cases_good(string: str) -> None:
    g.bool_expr.parse_string(string, parse_all=True)


@pytest.mark.parametrize(
    "string",
    [
        # Invalid operators
        "a.b === 1",
        "a.b ==",
        "a.b !=",
        # Double or missing dots
        "a..b",
        ".a.b",
        "a.b.",
        # Space after dot (adjacency violation)
        "a. b",
        "foo. bar == 1",
        # Dangling operators
        "not",
        "a.b == 1 and",
        "a.b == 1 or",
        # Keywords as full identifiers (not operators)
        "and.b == 1",
        "or.b == 1",
        "not.b == 1",
    ],
)
def test_bool_expr_edge_cases_bad(string: str) -> None:
    assert_parse_exception(make_parser(g.bool_expr), string)
