from typing import TYPE_CHECKING

import pyparsing as pp
from pydantic import BaseModel, model_validator
from pyparsing import ParseException

from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.conditions.grammar import parse_value_expr

if TYPE_CHECKING:
    from llm_gamebook.story.conditions.evaluator import BoolExprEvaluator


class ValueExprDefinition(BaseModel):
    """A dynamic value expression for an entity field.

    A string prefixed with '=' (e.g. `"=player.max_hp - player.injury"`) is
    parsed into a value expression AST. The source string is preserved for
    diagnostics. Field values hold a single expression (no list form).
    """

    value: g.Expr
    source: str

    @model_validator(mode="before")
    @classmethod
    def parse_value(cls, data: object) -> object:
        if isinstance(data, str):
            if not data.startswith("="):
                msg = f"Value expressions must be prefixed with '=', got: {data!r}"
                raise ValueError(msg)
            try:
                return {"value": parse_value_expr(data), "source": data}
            except ValueError as err:
                msg = f"Invalid value expression {data!r}: {err}"
                raise ValueError(msg) from err

        return data

    def __str__(self) -> str:
        """Return the source expression (accidental string use is visibly wrong)."""
        return self.source


class BoolExprDefinition(BaseModel):
    """A dynamic boolean expression.

    Examples:
    - boolean literal (e.g. `true` or `false`)
    - a single boolean expression (e.g. `"foo.a or bar.b"`, `"foo.a and bar.b"`, `"not foo.a"`), or
    - a list of expressions which are interpreted with logical AND (e.g. `["foo.a", "bar.b"]`).
    """

    # Put list first, otherwise ["...", "..."] would get coerced to `g.AndExpr`
    value: list[g.BoolExpr] | g.BoolExpr

    @model_validator(mode="before")
    @classmethod
    def parse_condition(cls, data: object) -> object:
        # Use StringStart/StringEnd to enforce full match
        full_parser = pp.StringStart() + g.bool_expr + pp.StringEnd()

        # Raw boolean (e.g. `enabled: true`)
        if isinstance(data, bool):
            return {"value": g.BoolLiteral(data)}

        #  String expression (e.g. `enabled: foo.bar > 1`)
        if isinstance(data, str):
            try:
                return {"value": full_parser.parse_string(data)[0]}
            except ParseException as err:
                raise ValueError(err.explain()) from err

        # List of expressions (e.g. `enabled: ["foo", true, 5]`)
        if isinstance(data, list):
            parsed_list: list[object] = []
            for el in data:
                try:
                    # YAML might have parsed these types natively.
                    # We wrap them in our Grammar Literals to satisfy g.BoolExpr type.
                    if isinstance(el, bool):
                        parsed_list.append(g.BoolLiteral(el))
                    elif isinstance(el, int):
                        parsed_list.append(g.IntLiteral(el))
                    elif isinstance(el, float):
                        parsed_list.append(g.FloatLiteral(el))
                    elif isinstance(el, str):
                        parsed_list.append(full_parser.parse_string(el)[0])
                    else:
                        msg = f"Unsupported type in list: {type(el)}"
                        raise ValueError(msg)  # noqa: TRY004
                except ParseException as err:
                    raise ValueError(err.explain()) from err

            return {"value": parsed_list}

        return data

    def evaluate(self, evaluator: "BoolExprEvaluator") -> bool:
        """Evaluate the expression with the given bound evaluator.

        Args:
            evaluator: The expression evaluator bound to a project and context.

        Returns:
            True if all sub-expressions (list form) or the single expression
            evaluates to true.
        """
        # If it's a list, we evaluate with AND logic (all must be true)
        if isinstance(self.value, list):
            return all(evaluator.eval(expr) for expr in self.value)

        return evaluator.eval(self.value)
