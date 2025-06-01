import string
import typing

import pyparsing as pp

pp.ParserElement.enable_packrat()


# Literals
class StrLiteral(typing.NamedTuple):
    value: str


class IntLiteral(typing.NamedTuple):
    value: int


class FloatLiteral(typing.NamedTuple):
    value: float


class BoolLiteral(typing.NamedTuple):
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
class SnakeCase(typing.NamedTuple):
    value: str


snake_case_segment = pp.Word(string.ascii_lowercase, string.ascii_lowercase + string.digits)
snake_case = pp.Combine(
    snake_case_segment + pp.ZeroOrMore(pp.Literal("_") + snake_case_segment)
).set_parse_action(lambda t: SnakeCase(t[0]))


# Dot path
class DotPath(typing.NamedTuple):
    """`entity_id.property[.property[...]]`"""

    entity_id: SnakeCase
    property_chain: tuple[SnakeCase, ...]


dot_path = (snake_case + pp.OneOrMore(pp.Literal(".").suppress() + snake_case)).set_parse_action(
    lambda t: DotPath(t[0], tuple(t[1:]))
)


# Comparison
class ComparisonOperator(typing.NamedTuple):
    value: typing.Literal["==", "!=", "<", "<=", ">", ">=", "in"]


class Comparison(typing.NamedTuple):
    left: DotPath | Literal
    op: ComparisonOperator
    right: DotPath | Literal


comp_op = pp.one_of("== != < <= > >= in").set_parse_action(lambda t: ComparisonOperator(t[0]))
comp_operand = dot_path | literal
comparison = (comp_operand + comp_op + comp_operand).set_parse_action(
    lambda t: Comparison(t[0], t[1], t[2])
)


# Boolean expression grammar
class NotExpr(typing.NamedTuple):
    expr: "BoolExpr"


class AndExpr(typing.NamedTuple):
    left: "BoolExpr"
    right: "BoolExpr"


class OrExpr(typing.NamedTuple):
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
