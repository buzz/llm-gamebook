from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Annotated, Literal, Protocol, TypedDict

from pydantic import AfterValidator

from llm_gamebook.schema.validators import (
    is_normalized_pascal_case,
    is_normalized_snake_case,
)

if TYPE_CHECKING:
    from pydantic_ai.tools import Tool

    from llm_gamebook.story.state import StoryState

type StoryTool = Tool[StoryState]
"""A LLM tool function."""

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


class UserInterface(Protocol):
    def text_response(self, think_text: str | None, text: str | None) -> None: ...

    def tool_call(self, tool_name: str, tool_args: str) -> None: ...

    @contextmanager
    def stream_printer(self) -> Iterator[Callable[[str], None]]: ...

    async def get_user_input(self) -> str: ...
