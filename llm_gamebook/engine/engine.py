import logging
import random
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.engine.messages import MessageList
from llm_gamebook.logger import logger
from llm_gamebook.story.state import StoryState

if TYPE_CHECKING:
    from llm_gamebook.types import UserInterface


class StoryEngine:
    def __init__(
        self, model: Model, state: StoryState, ui: "UserInterface", *, streaming: bool = True
    ) -> None:
        self._log = logger.getChild("engine")
        self._state = state
        self._ui = ui
        self._streaming = streaming
        self._messages = MessageList(self._state)
        self._run_count = 0
        self._agent = Agent[StoryState, str](
            model,
            deps_type=StoryState,
            model_settings=ModelSettings(seed=random.randint(0, 10000), temperature=0.8),
            output_type=str,
            tools=list(self._state.get_tools()),
            prepare_tools=self._prepare_tools,
        )

    async def story_loop(self) -> None:
        user_input: str | None = None

        while True:
            # Run agent
            message_history = await self._messages.get(user_input)

            if self._is_debug:
                self._messages._debug_log_messages(message_history)

            new_messages, _ = await self._run(message_history)

            self._messages.append(user_input, new_messages)
            self._run_count += 1

            # Get user message
            if not self._messages.last_message_was_tool_return:
                user_input = await self._ui.get_user_input()
                if user_input == "quit":
                    break

    async def _run(
        self, message_history: list[ModelMessage]
    ) -> tuple[Sequence[ModelMessage], Sequence[ModelMessage]]:
        if self._streaming:
            async with self._agent.run_stream(
                message_history=message_history, deps=self._state
            ) as streamed_result:
                with self._ui.stream_printer() as handle:
                    async for message in streamed_result.stream_text(delta=True):
                        handle(message)
            self._print_tool_call(streamed_result.new_messages())
            return streamed_result.new_messages(), streamed_result.all_messages()

        # non-streaming
        result = await self._agent.run(message_history=message_history, deps=self._state)
        self._print_tool_call(result.new_messages())
        self._print_model_response(result.new_messages())
        return result.new_messages(), result.all_messages()

    async def _prepare_tools(
        self,
        ctx: RunContext[StoryState],
        tools: list[ToolDefinition],
    ) -> list[ToolDefinition] | None:
        # No tools for introductory message
        return tools if len(ctx.messages) > 2 else None

    def _print_tool_call(self, messages: Iterable[ModelMessage]) -> None:
        for msg in messages:
            if isinstance(msg, ModelResponse) and len(msg.parts) > 0:
                for part in msg.parts:
                    if isinstance(part, ToolCallPart):
                        self._ui.tool_call(part.tool_name, part.args_as_json_str())

    def _print_model_response(self, messages: Iterable[ModelMessage]) -> None:
        for msg in messages:
            if isinstance(msg, ModelResponse) and len(msg.parts) > 0:
                for part in msg.parts:
                    if isinstance(part, TextPart) and part.has_content():
                        self._ui.text_response(*MessageList.parse_reasoning(part.content))

    @property
    def _is_debug(self) -> bool:
        return self._log.getEffectiveLevel() == logging.DEBUG
