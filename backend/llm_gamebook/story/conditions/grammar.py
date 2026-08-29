import typing
from dataclasses import dataclass
from typing import cast

import pyparsing as pp

pp.ParserElement.enable_packrat()

type ComparisonOperatorValue = typing.Literal["==", "!=", "<", "<=", ">", ">=", "in"]
type ArithOperatorValue = typing.Literal["+", "-", "*", "/"]


# Literals
@dataclass(frozen=True)
class StrLiteral:
    value: str


@dataclass(frozen=True)
class IntLiteral:
    value: int


@dataclass(frozen=True)
class FloatLiteral:
    value: float


@dataclass(frozen=True)
class BoolLiteral:
    value: bool


Literal = StrLiteral | IntLiteral | FloatLiteral | BoolLiteral

string_literal = pp.quoted_string.set_parse_action(pp.remove_quotes, lambda t: StrLiteral(t[0]))
float_literal = pp.Regex(r"\d+\.\d+").set_parse_action(lambda t: FloatLiteral(float(t[0])))
integer_literal = pp.Regex(r"\d+").set_parse_action(lambda t: IntLiteral(int(t[0])))
bool_literal = (pp.Keyword("true") | pp.Keyword("false")).set_parse_action(
    lambda t: BoolLiteral(t[0].lower() == "true")
)
literal = string_literal | float_literal | integer_literal | bool_literal


# snake_case
@dataclass(frozen=True)
class SnakeCase:
    value: str


# Use Regex with negative lookahead to exclude keywords (not, and, or).
# The \b word boundary ensures keywords are rejected regardless of what follows
# (e.g., "not.b" fails because "not" is followed by a word boundary).
_snake_case_raw = pp.Regex(r"(?!not\b|and\b|or\b)[a-z]+(_[a-z]+)*")

snake_case = _snake_case_raw.copy().set_parse_action(lambda t: SnakeCase(t[0]))


# Dot path
@dataclass(frozen=True)
class DotPath:
    """`entity_id.property[.property[.property[...]]]`"""

    entity_id: SnakeCase
    property_chain: tuple[SnakeCase, ...]


# Using pp.Combine enforces adjacency between tokens (no whitespace allowed).
# If "foo_bar .id" is parsed, Combine fails due to the space, raising ParseException.
# The dot is NOT suppressed, so Combine merges it into a single string "foo.bar".
# We then split the string in the parse action to reconstruct the DotPath object.
dot_path = pp.Combine(
    _snake_case_raw + pp.OneOrMore(pp.Literal(".") + _snake_case_raw)
).set_parse_action(
    lambda t: DotPath(
        entity_id=SnakeCase(t[0].split(".")[0]),
        property_chain=tuple(SnakeCase(p) for p in t[0].split(".")[1:]),
    )
)


# Comparison
@dataclass(frozen=True)
class ComparisonOperator:
    value: ComparisonOperatorValue


@dataclass(frozen=True)
class Comparison:
    left: "Expr"
    op: ComparisonOperator
    right: "Expr"


comp_op = pp.one_of("== != < <= > >= in").set_parse_action(lambda t: ComparisonOperator(t[0]))
comp_operand = dot_path | literal


def create_comparison(t: pp.ParseResults) -> object:
    """Infix-level parse action producing a Comparison node.

    The infix level wraps the [left, op, right] tokens in a Group, so they
    arrive as a single inner token list (t[0]).

    Comparisons are non-associative: a chained comparison (e.g. `a < b < c`)
    fails the parse. pyparsing' infix levels are left-associative, so chains
    reach this parse action with more than 3 tokens and are rejected there.
    """
    tokens = t[0]
    if len(tokens) > 3:
        msg = "Chained comparisons are not allowed"
        raise pp.ParseException(msg)
    return Comparison(tokens[0], tokens[1], tokens[2])


# Standalone comparison non-terminal (a comparison of two plain operands).
comparison = (comp_operand + comp_op + comp_operand).set_parse_action(
    lambda t: Comparison(t[0], t[1], t[2])
)


# Arithmetic
@dataclass(frozen=True)
class ArithOperator:
    value: ArithOperatorValue


@dataclass(frozen=True)
class ArithExpr:
    """A binary arithmetic operation (left operator right)."""

    left: "Expr"
    operator: ArithOperator
    right: "Expr"


def create_arith_expr(t: pp.ParseResults) -> object:
    """Parse action building a left-associative chain of ArithExpr nodes.

    Args:
        t: Parse results; t[0] is the token list [term, op, term, op, term...]
        with operands first and operator strings in between. An operand that
        came from a higher-precedence level is already a single node object.

    Returns:
        The nested ArithExpr AST (or the single operand for a lone term).
    """
    tokens = t[0]
    expr = tokens[0]
    # Operators sit at odd indices; each one combines the running result with
    # the following operand (left-associative).
    for i in range(1, len(tokens), 2):
        expr = ArithExpr(left=expr, operator=ArithOperator(tokens[i]), right=tokens[i + 1])
    return expr


# Value expression grammar (unified; conditions are the boolean specialization)
@dataclass(frozen=True)
class NotExpr:
    expr: "Expr"


@dataclass(frozen=True)
class AndExpr:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class OrExpr:
    left: "Expr"
    right: "Expr"


Expr = Literal | DotPath | ArithExpr | Comparison | NotExpr | AndExpr | OrExpr

# Boolean conditions share the value expression grammar.
BoolExpr = Expr


def create_binary_expr(op_class: type[AndExpr | OrExpr]) -> pp.ParseAction:
    def parse_action(t: pp.ParseResults) -> object:
        # t[0] is the list of tokens: [op1, 'and', op2, 'and', op3...]
        # We start with the left-most operand
        tokens = t[0]
        expr = tokens[0]
        # Iterate over the rest in steps of 2 (skipping the operator string)
        for i in range(2, len(tokens), 2):
            right = tokens[i]
            expr = op_class(left=expr, right=right)
        return expr

    return parse_action


def create_unary_expr(op_class: type[NotExpr]) -> pp.ParseAction:
    def parse_action(t: pp.ParseResults) -> object:
        tokens = t[0]
        # The operand is the last element
        expr = tokens[-1]
        # The operators are everything before the last element
        # We iterate backwards or simply wrap for every 'not' found
        operator_count = len(tokens) - 1

        for _ in range(operator_count):
            expr = op_class(expr=expr)

        return expr

    return parse_action


expr = pp.Forward()
# `bool_expr` is an alias of `expr`: conditions and field values share one grammar.
bool_expr = expr

expr <<= pp.infix_notation(
    dot_path | literal | (pp.Suppress(pp.Literal("(")) + expr + pp.Suppress(pp.Literal(")"))),
    [
        (pp.one_of("* /"), 2, pp.opAssoc.LEFT, create_arith_expr),
        (pp.one_of("+ -"), 2, pp.opAssoc.LEFT, create_arith_expr),
        (comp_op, 2, pp.opAssoc.LEFT, create_comparison),
        (pp.Keyword("not"), 1, pp.opAssoc.RIGHT, create_unary_expr(NotExpr)),
        (pp.Keyword("and"), 2, pp.opAssoc.LEFT, create_binary_expr(AndExpr)),
        (pp.Keyword("or"), 2, pp.opAssoc.LEFT, create_binary_expr(OrExpr)),
    ],
)

_full_expr_parser = pp.StringStart() + expr + pp.StringEnd()


def _parse_full_match(expression: str) -> Expr:
    """Parse a full-match expression and wrap parse failures in ValueError."""
    try:
        return cast("Expr", _full_expr_parser.parse_string(expression)[0])
    except pp.ParseException as err:
        raise ValueError(err.explain()) from err


def parse_bool_expr(expression: str) -> BoolExpr:
    """Parse a boolean expression string into a BoolExpr AST.

    An optional leading "=" (dynamic expression marker) is stripped before
    parsing, e.g. "=foo.bar == 'x'" parses like "foo.bar == 'x'".

    Args:
        expression: The expression string to parse.

    Returns:
        The parsed boolean expression AST.

    Raises:
        ValueError: If the expression cannot be parsed.
    """
    return _parse_full_match(expression.removeprefix("="))


def parse_value_expr(expression: str) -> Expr:
    """Parse a value expression string into an Expr AST.

    An optional leading "=" (dynamic expression marker) is stripped before
    parsing, e.g. "=foo.bar + 1" parses like "foo.bar + 1".

    Args:
        expression: The expression string to parse.

    Returns:
        The parsed value expression AST.

    Raises:
        ValueError: If the expression cannot be parsed.
    """
    return _parse_full_match(expression.removeprefix("="))
