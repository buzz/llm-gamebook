from collections.abc import AsyncIterable, Sequence
from typing import TYPE_CHECKING

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelResponsePart,
    SystemPromptPart,
    TextPart,
    ToolReturnPart,
    UserPromptPart,
)

from llm_gamebook.logger import logger
from llm_gamebook.utils import parse_reasoning

if TYPE_CHECKING:
    from llm_gamebook.story.state import StoryState


class MessageList:
    def __init__(self, state: "StoryState") -> None:
        self._log = logger.getChild("messages")
        self._state = state

        self._messages: list[ModelMessage] = []
        """The current message history (excluding the system prompt)."""

    async def get_messages(self, *, for_llm: bool) -> list[ModelMessage]:
        return [msg async for msg in self._generate_messages(for_llm=for_llm)]

    async def _generate_messages(self, *, for_llm: bool) -> AsyncIterable[ModelMessage]:
        yield await self._generate_initial_request()

        for msg in self._messages:
            if not msg.parts:
                continue

            if for_llm and isinstance(msg, ModelResponse):
                stripped_msg = self._strip_think_blocks(msg)
                if stripped_msg.parts:
                    yield stripped_msg

            else:
                yield msg

    async def _generate_initial_request(self) -> ModelRequest:
        system_prompt = await self._state.get_system_prompt()
        message = ModelRequest([SystemPromptPart(content=system_prompt)])
        message.parts.append(UserPromptPart(content=await self._state.get_intro_message()))
        return message

    def append(self, new_messages: Sequence[ModelMessage]) -> None:
        self._messages += new_messages

    def append_user_prompt(self, user_input: str) -> None:
        self._messages.append(ModelRequest([UserPromptPart(user_input)]))

    @property
    def last_message_was_tool_return(self) -> bool:
        return isinstance(self._messages[-1].parts[-1], ToolReturnPart)

    @classmethod
    def _strip_think_blocks(cls, msg: ModelResponse) -> ModelMessage:
        new_parts: list[ModelResponsePart] = []
        for part in msg.parts:
            if isinstance(part, TextPart):
                _, response_text = parse_reasoning(part.content)
                if response_text:
                    part.content = response_text
                    new_parts.append(part)
            else:
                new_parts.append(part)
        msg.parts = new_parts
        return msg
