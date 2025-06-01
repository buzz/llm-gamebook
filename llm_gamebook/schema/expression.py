from typing import TYPE_CHECKING, Any, assert_never, get_args

from pydantic import BaseModel, model_validator
from pyparsing import ParseException

from llm_gamebook.story.conditions.evaluator import eval_bool_expr
from llm_gamebook.story.conditions.expression import BoolExpr, Literal, bool_expr

if TYPE_CHECKING:
    from collections.abc import Mapping

    from llm_gamebook.story.entity import BaseStoryEntity


class BooleanExpression(BaseModel):
    value: bool | BoolExpr | list[BoolExpr]

    @model_validator(mode="before")
    @classmethod
    def parse_condition(cls, data: Any) -> Any:
        try:
            if isinstance(data, str):
                return {"value": bool_expr.parse_string(data)[0]}
            if isinstance(data, list):
                if not all(isinstance(el, str) for el in data):
                    msg = "Expected all elements of list to be of type str"
                    raise ValueError(msg)
                return {"value": [bool_expr.parse_string(el)[0] for el in data]}
        except ParseException as err:
            raise ValueError(err.explain()) from err

        return data

    def evaluate(self, entities: "Mapping[str, BaseStoryEntity]") -> bool:
        if isinstance(self.value, bool):
            return self.value
        if isinstance(self.value, Literal):
            return bool(self.value)
        if isinstance(self.value, list):
            return all(eval_bool_expr(expr, entities) for expr in self.value)
        if isinstance(self.value, BoolExpr):
            return eval_bool_expr(self.value, entities)

        assert_never(self.value)
