import logging
import random
import re
from collections.abc import Iterable, Sequence

from colorama import Style
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, SystemPromptPart, TextPart, ToolCallPart
from pydantic_ai.models import Model, ModelSettings

from llm_gamebook.example import example_story_context
from llm_gamebook.logger import logger
from llm_gamebook.story.context import StoryContext


class GameEngine:
    def __init__(self, model: Model) -> None:
        self._log = logger.getChild("engine")
        self._messages: list[ModelMessage] = []
        self._story_context = example_story_context()
        self._agent = self._setup_agent(model)
        self._is_running = True

    def _setup_agent(self, model: Model) -> Agent[StoryContext, str]:
        agent = Agent[StoryContext, str](
            model,
            deps_type=StoryContext,
            model_settings=ModelSettings(seed=random.randint(0, 10000)),
            output_type=str,
            tools=self._story_context.tools,
        )

        # Makes the system prompt reevaluate on every run
        @agent.system_prompt(dynamic=True)
        async def get_system_prompt() -> str:
            return await self._story_context.get_system_prompt()

        return agent

    async def game_loop(self) -> None:
        while self._is_running:
            user_prompt: str | None = None
            if len(self._messages) == 0:
                user_prompt = await self._story_context.get_first_message()
            elif isinstance(self._messages[-1], ModelResponse):
                user_prompt = input("> ")
            else:
                user_prompt = None

            if user_prompt == "quit":
                self._is_running = False
                break

            async with self._agent.run_stream(
                user_prompt,
                message_history=self._messages,
                deps=self._story_context,
            ) as result:
                # Print stream
                if self._is_debug:
                    print(f"Streaming: {Style.DIM}", end="")
                async for message in result.stream_text(delta=True):
                    if self._is_debug:
                        print(message, end="", flush=True)
                if self._is_debug:
                    print(Style.RESET_ALL)

            if self._is_debug:
                self._debug_log_messages(result.all_messages())

            self._print_model_response(result.new_messages())
            self._messages = list(self._strip_think_blocks(result.all_messages()))

    def _print_model_response(self, messages: Iterable[ModelMessage]) -> None:
        for msg in messages:
            if isinstance(msg, ModelResponse) and len(msg.parts) > 0:
                for part in msg.parts:
                    if isinstance(part, TextPart) and part.has_content():
                        _, response_text = self._parse_reasoning(part.content)
                        if response_text:
                            print(f"\n{Style.BRIGHT}{response_text}{Style.RESET_ALL}\n")
                    elif isinstance(part, ToolCallPart):
                        print(
                            f"\n{Style.DIM}Tool call: {part.tool_name}({part.args_as_json_str()}){Style.RESET_ALL}\n",
                        )

    def _debug_log_messages(self, messages: Sequence[ModelMessage]) -> None:
        self._log.debug("Messages (total=%d)", len(messages))
        for idx, msg in enumerate(messages):
            self._log.debug("%03d. %s", idx, type(msg).__name__)
            for part in msg.parts:
                if isinstance(part, SystemPromptPart):
                    self._log.debug("  - System: %s", part.content)
                # elif isinstance(part, UserPromptPart):
                #     self._log.debug("  - User: %s", part.content)
                # elif isinstance(part, TextPart):
                #     self._log.debug("  - Assistant")
                #     think_block, response_text = self._parse_reasoning(part.content)
                #     self._log.debug("    - think: %s", think_block)
                #     self._log.debug("    - response: %s", response_text)
                # elif isinstance(part, ToolCallPart):
                #     self._log.debug("  - Tool call: `%s` args=%s", part.tool_name, part.args)
                # elif isinstance(part, ToolReturnPart):
                #     self._log.debug("  - Tool return: `%s` args=%s", part.tool_name, part.content)
                # else:
                #     self._log.debug("  - Unknown part: %s", part)

    def _strip_think_blocks(self, messages: Iterable[ModelMessage]) -> Iterable[ModelMessage]:
        for msg in messages:
            if isinstance(msg, ModelResponse) and len(msg.parts) > 0:
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        _, response_text = self._parse_reasoning(part.content)
                        part.content = response_text or ""
            yield msg

    @staticmethod
    def _parse_reasoning(text: str) -> tuple[str | None, str | None]:
        match = re.search(r"<think>\s*(.*?)\s*</think>\s*(.*)", text, re.DOTALL)
        if match:
            think_block = match.group(1) or None
            msg = match.group(2).strip() or None
            return think_block, msg
        return None, text.strip() or None

    @property
    def _is_debug(self) -> bool:
        return self._log.getEffectiveLevel() == logging.DEBUG
