from typing import TYPE_CHECKING, Self

from pydantic_ai import RunContext
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.story import PromptGenerator, StoryState

if TYPE_CHECKING:
    from collections.abc import Iterable

    from llm_gamebook.types import StoryTool


class StoryContext:
    def __init__(self, state: StoryState) -> None:
        self.state = state
        self.prompt_generator = PromptGenerator(state)

    def get_tools(self) -> "Iterable[StoryTool]":
        for entity_type in self.state.entity_types.values():
            yield from entity_type.get_tools()

    async def prepare_tools(
        self,
        ctx: RunContext[Self],
        tools: list[ToolDefinition],
    ) -> list[ToolDefinition] | None:
        if len(ctx.messages) <= 1:
            # No tools for introductory message
            return None
        return tools
