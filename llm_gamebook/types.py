from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Literal, Protocol, TypedDict

from pydantic import AfterValidator
from pydantic_ai.messages import ModelMessage

from llm_gamebook.schema.validators import (
    is_normalized_pascal_case,
    is_normalized_snake_case,
)

if TYPE_CHECKING:
    from pydantic_ai.tools import Tool

    from llm_gamebook.engine.engine import StreamState
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
    def messages_update(self, messages: list[ModelMessage]) -> None: ...

    def stream_state_update(self, state: "StreamState", text: str | None = None) -> None: ...

    async def get_user_input(self) -> str: ...

    def set_shutdown_callable(self, func: Callable[[], None]) -> None: ...

    def shutdown(self) -> None: ...
