from typing import TYPE_CHECKING, Any, assert_never

from pydantic import BaseModel, model_validator
from pyparsing import ParseException

from llm_gamebook.story.conditions import BoolExprEvaluator
from llm_gamebook.story.conditions import bool_expr_grammar as g

if TYPE_CHECKING:
    from llm_gamebook.story.project import Project


class BoolExprDefinition(BaseModel):
    """A dynamic boolean expression.

    Can be a boolean literal, a single boolean expression, or a list of expressions combined with
    logical AND.
    """

    value: bool | g.BoolExpr | list[g.BoolExpr]

    @model_validator(mode="before")
    @classmethod
    def parse_condition(cls, data: Any) -> Any:
        try:
            if isinstance(data, str):
                return {"value": g.bool_expr.parse_string(data)[0]}
            if isinstance(data, list):
                if not all(isinstance(el, str) for el in data):
                    msg = "Expected all elements of list to be of type str"
                    raise ValueError(msg)
                return {"value": [g.bool_expr.parse_string(el)[0] for el in data]}
        except ParseException as err:
            raise ValueError(err.explain()) from err

        return data

    def evaluate(self, project: "Project") -> bool:
        if isinstance(self.value, bool):
            return self.value
        if isinstance(self.value, g.Literal):
            return bool(self.value)

        evaluator = BoolExprEvaluator(project)

        if isinstance(self.value, list):
            # Lists of expressions are combined using AND
            return all(evaluator.eval(expr) for expr in self.value)
        if isinstance(self.value, g.BoolExpr):
            return evaluator.eval(self.value)

        assert_never(self.value)
