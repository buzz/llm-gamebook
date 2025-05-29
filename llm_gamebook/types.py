from typing import TYPE_CHECKING, Literal, TypedDict

from pydantic_ai.tools import Tool

if TYPE_CHECKING:
    from llm_gamebook.engine.context import StoryContext

type StoryTool = Tool[StoryContext]


class FunctionSuccessResult(TypedDict):
    result: Literal["success"]


class FunctionErrorResult(TypedDict):
    result: Literal["error"]
    reason: str | None


FunctionResult = FunctionSuccessResult | FunctionErrorResult
