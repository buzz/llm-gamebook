import logging
import random
from collections.abc import AsyncIterator, Iterable, Sequence
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from colorama import Fore
from pydantic_ai import Agent, RunContext
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.result import StreamedRunResult
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
        self._messages = MessageList()
        self._agent = self._setup_agent(model)
        self._is_running = True

    def _setup_agent(self, model: Model) -> Agent[StoryState, str]:
        agent = Agent[StoryState, str](
            model,
            deps_type=StoryState,
            model_settings=ModelSettings(seed=random.randint(0, 10000), temperature=0.8),
            output_type=str,
            tools=list(self._state.get_tools()),
            prepare_tools=self._prepare_tools,
        )

        # Makes the system prompt reevaluate on every run
        @agent.system_prompt(dynamic=True)
        async def get_system_prompt() -> str:
            return await self._state.get_system_prompt()

        return agent

    async def story_loop(self) -> None:
        while self._is_running:
            user_prompt = await self._get_user_prompt()

            if user_prompt == "quit":
                self._is_running = False
                break

            if self._streaming:
                async with self._run_stream(user_prompt) as streamed_result:
                    with self._ui.stream_printer() as handle:
                        async for message in streamed_result.stream_text(delta=True):
                            handle(message)
                self._print_tool_call(streamed_result.new_messages())
                self._messages.set(streamed_result.all_messages())
            else:
                result = await self._run(user_prompt)
                self._print_tool_call(result.new_messages())
                self._print_model_response(result.new_messages())
                self._messages.set(result.all_messages())

            if self._is_debug:
                self._debug_log_messages(self._messages)

            self._messages.strip_think_blocks()

    async def _get_user_prompt(self) -> str | None:
        if len(self._messages) == 0:
            return await self._state.get_first_message()
        if isinstance(self._messages[-1], ModelResponse):
            return await self._ui.get_user_input()
        return None

    @asynccontextmanager
    async def _run_stream(
        self, user_prompt: str | None
    ) -> AsyncIterator[StreamedRunResult[StoryState, str]]:
        async with self._agent.run_stream(
            user_prompt, message_history=self._messages.get(), deps=self._state
        ) as result:
            yield result

    async def _run(self, user_prompt: str | None) -> AgentRunResult[str]:
        return await self._agent.run(
            user_prompt, message_history=self._messages.get(), deps=self._state
        )

    async def _prepare_tools(
        self,
        ctx: RunContext[StoryState],
        tools: list[ToolDefinition],
    ) -> list[ToolDefinition] | None:
        if len(ctx.messages) <= 1:
            # No tools for introductory message
            return None
        return tools

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

    def _debug_log_messages(self, messages: Sequence[ModelMessage]) -> None:
        self._log.debug("\n%sMessages (total=%d)%s\n", Fore.MAGENTA, len(messages), Fore.RESET)

        for idx, msg in enumerate(messages):
            self._log.debug("%s%03d. %s%s", Fore.MAGENTA, idx, type(msg).__name__, Fore.RESET)
            for part in msg.parts:
                if isinstance(part, SystemPromptPart):
                    self._log.debug("  - System: %s", part.content)
                elif isinstance(part, UserPromptPart):
                    self._log.debug("  - User: %s", part.content)
                elif isinstance(part, TextPart):
                    self._log.debug("  - Assistant")
                    think_block, text = MessageList.parse_reasoning(part.content)
                    if think_block:
                        self._log.debug("    - think: %s", think_block)
                    if text:
                        self._log.debug("    - response: %s", text)
                elif isinstance(part, ToolCallPart):
                    self._log.debug("  - Tool call: `%s` args=%s", part.tool_name, part.args)
                elif isinstance(part, ToolReturnPart):
                    self._log.debug("  - Tool return: `%s` args=%s", part.tool_name, part.content)
                self._log.debug("\n")

    @property
    def _is_debug(self) -> bool:
        return self._log.getEffectiveLevel() == logging.DEBUG
