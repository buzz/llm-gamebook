import contextlib
from pyexpat import model
import re
import textwrap
from collections.abc import AsyncIterable, Sequence
from dataclasses import field
from typing import TYPE_CHECKING, Annotated, overload
from uuid import UUID, uuid4

import pydantic
import pydantic_ai.messages as pai
from colorama import Fore

from llm_gamebook.logger import logger

if TYPE_CHECKING:
    from llm_gamebook.story.state import StoryState

think_block_re = re.compile(r"<think>\s*(.*?)\s*</think>\s*(.*)", re.DOTALL)


class UuidMixin:
    uuid: UUID = field(default_factory=uuid4)


class ModelRequest(pai.ModelRequest, UuidMixin):
    pass


class ModelResponse(pai.ModelResponse, UuidMixin):
    pass


ModelMessage = Annotated[ModelRequest | ModelResponse, pydantic.Discriminator("kind")]


class MessageList(Sequence[ModelMessage]):
    def __init__(self, state: "StoryState") -> None:
        self._log = logger.getChild("messages")
        self._state = state

        self._messages: list[ModelMessage] = []
        """The current message history (excluding the system prompt)."""

    async def get(self, user_input: str | None = None) -> list[pai.ModelMessage]:
        return [msg async for msg in self._generate_messages(user_input)]

    async def _generate_messages(self, user_input: str | None) -> AsyncIterable[ModelMessage]:
        if user_input and len(self._messages) == 0:
            err_msg = "User input was supplied on first run"
            raise RuntimeError(err_msg)

        yield await self._generate_initial_request(add_intro_message=len(self._messages) == 0)
        for msg in self._messages:
            if isinstance(msg, ModelResponse):
                stripped_msg = self._strip_think_blocks(msg)
                if stripped_msg.parts:
                    yield stripped_msg
            else:
                yield msg

        if user_input:
            yield await self._generate_user_prompt(user_input)

    async def _generate_initial_request(self, *, add_intro_message: bool = False) -> ModelRequest:
        system_prompt = await self._state.get_system_prompt()
        parts: list[pai.ModelRequestPart] = [pai.SystemPromptPart(content=system_prompt)]
        if add_intro_message:
            parts.append(pai.UserPromptPart(content=await self._state.get_intro_message()))
        return ModelRequest(parts)

    async def _generate_user_prompt(self, user_input: str) -> ModelRequest:
        prompt = await self._state.get_user_prompt(user_input)
        return ModelRequest([pai.UserPromptPart(prompt)])

    def append(self, user_input: str | None, new_messages: Sequence[pai.ModelMessage]) -> None:
        if user_input:
            self._messages.append(ModelRequest([pai.UserPromptPart(user_input)]))
        for msg in new_messages:
            if isinstance(msg, pai.ModelResponse) and msg.parts:
                resp = ModelResponse(msg.parts, msg.usage, msg.model_name, msg.timestamp)
                self._messages.append(resp)
            elif isinstance(msg, pai.ModelRequest):
                with contextlib.suppress(IndexError):
                    if isinstance(msg.parts[0], pai.ToolReturnPart):
                        self._messages.append(ModelRequest(msg.parts, msg.instructions))

    @property
    def last_message_was_tool_return(self) -> bool:
        return isinstance(self._messages[-1].parts[-1], pai.ToolReturnPart)

    @classmethod
    def _strip_think_blocks(cls, msg: ModelResponse) -> ModelMessage:
        new_parts: list[pai.ModelResponsePart] = []
        for part in msg.parts:
            if isinstance(part, pai.TextPart):
                _, response_text = cls.parse_reasoning(part.content)
                if response_text:
                    part.content = response_text
                    new_parts.append(part)
            else:
                new_parts.append(part)
        msg.parts = new_parts
        return msg

    @staticmethod
    def parse_reasoning(text: str) -> tuple[str | None, str | None]:
        match = think_block_re.search(text)
        if match:
            think_block = match.group(1) or None
            msg = match.group(2).strip() or None
            return think_block, msg
        return None, text.strip() or None

    def _debug_log_messages(
        self, messages: Sequence[pai.ModelMessage], width: int | None = None
    ) -> None:
        self._log.debug("\n%sMessages (total=%d)%s\n", Fore.MAGENTA, len(messages), Fore.RESET)

        def shorten(text: str) -> str:
            return textwrap.shorten(text, width) if width else text

        for idx, msg in enumerate(messages):
            self._log.debug("%s%03d. %s%s", Fore.MAGENTA, idx, type(msg).__name__, Fore.RESET)
            for part in msg.parts:
                if isinstance(part, pai.SystemPromptPart):
                    self._log.debug("  - System: %s", shorten(part.content))
                elif isinstance(part, pai.UserPromptPart):
                    if isinstance(part.content, str):
                        self._log.debug("  - User: %s", shorten(part.content))
                elif isinstance(part, pai.TextPart):
                    self._log.debug("  - Assistant")
                    think_block, text = MessageList.parse_reasoning(part.content)
                    if think_block:
                        self._log.debug("    - think: %s", shorten(think_block))
                    if text:
                        self._log.debug("    - response: %s", shorten(text))
                elif isinstance(part, pai.ToolCallPart):
                    self._log.debug("  - Tool call: `%s` args=%s", part.tool_name, part.args)
                elif isinstance(part, pai.ToolReturnPart):
                    self._log.debug("  - Tool return: `%s` args=%s", part.tool_name, part.content)
                self._log.debug("\n")

    def __len__(self) -> int:
        return len(self._messages)

    @overload
    def __getitem__(self, index: int) -> ModelMessage: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[ModelMessage]: ...
    def __getitem__(self, index: int | slice) -> ModelMessage | Sequence[ModelMessage]:
        return self._messages[index]
