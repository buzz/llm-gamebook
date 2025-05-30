from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Literal, Protocol, TypedDict

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


class UserInterface(Protocol):
    def text_response(self, think_text: str | None, text: str | None) -> None: ...

    def tool_call(self, tool_name: str, tool_args: str) -> None: ...

    @contextmanager
    def stream_printer(self) -> Iterator[Callable[[str], None]]: ...

    async def get_user_input(self) -> str: ...
