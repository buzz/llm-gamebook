from typing import TYPE_CHECKING, Annotated, Literal, TypedDict

from pydantic import AfterValidator

from llm_gamebook.schema.validators import is_normalized_pascal_case, is_normalized_snake_case

if TYPE_CHECKING:
    from pydantic_ai.tools import Tool

    from .state import StoryState

type StoryTool = Tool[StoryState]
"""An LLM tool function."""

NormalizedPascalCase = Annotated[str, AfterValidator(is_normalized_pascal_case)]
"""PascalCase name with non-ASCII characters normalized."""

NormalizedSnakeCase = Annotated[str, AfterValidator(is_normalized_snake_case)]
"""snake_case name with non-ASCII characters normalized."""


class FunctionSuccessResult(TypedDict):
    result: Literal["success"]


class FunctionErrorResult(TypedDict):
    result: Literal["error"]
    reason: str | None


FunctionResult = FunctionSuccessResult | FunctionErrorResult
