from typing import TYPE_CHECKING

import pyparsing as pp
from pydantic import BaseModel, model_validator
from pyparsing import ParseException

from llm_gamebook.story.conditions import BoolExprEvaluator
from llm_gamebook.story.conditions import bool_expr_grammar as g

if TYPE_CHECKING:
    from llm_gamebook.story.project import Project


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

    def evaluate(self, project: "Project") -> bool:
        # If it's a list, we evaluate with AND logic (all must be true)
        if isinstance(self.value, list):
            evaluator = BoolExprEvaluator(project)
            return all(evaluator.eval(expr) for expr in self.value)

        evaluator = BoolExprEvaluator(project)
        return evaluator.eval(self.value)
