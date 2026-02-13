import typing
from dataclasses import dataclass

import pyparsing as pp

pp.ParserElement.enable_packrat()

type ComparisonOperatorValue = typing.Literal["==", "!=", "<", "<=", ">", ">=", "in"]


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
    left: DotPath | Literal
    op: ComparisonOperator
    right: DotPath | Literal


comp_op = pp.one_of("== != < <= > >= in").set_parse_action(lambda t: ComparisonOperator(t[0]))
comp_operand = dot_path | literal
comparison = (comp_operand + comp_op + comp_operand).set_parse_action(
    lambda t: Comparison(t[0], t[1], t[2])
)


# Boolean expression grammar
@dataclass(frozen=True)
class NotExpr:
    expr: "BoolExpr"


@dataclass(frozen=True)
class AndExpr:
    left: "BoolExpr"
    right: "BoolExpr"


@dataclass(frozen=True)
class OrExpr:
    left: "BoolExpr"
    right: "BoolExpr"


BoolExpr = Literal | DotPath | Comparison | NotExpr | AndExpr | OrExpr


bool_expr = pp.infix_notation(
    comparison | dot_path | literal,
    [
        (
            pp.Keyword("not"),
            1,
            pp.opAssoc.RIGHT,
            lambda t: NotExpr(t[0][1]),
        ),
        (
            pp.Keyword("and"),
            2,
            pp.opAssoc.LEFT,
            lambda t: AndExpr(t[0][0], t[0][2]),
        ),
        (
            pp.Keyword("or"),
            2,
            pp.opAssoc.LEFT,
            lambda t: OrExpr(t[0][0], t[0][2]),
        ),
    ],
)
