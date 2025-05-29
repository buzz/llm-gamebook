import re
from collections.abc import Sequence
from typing import overload

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart

think_block_re = re.compile(r"<think>\s*(.*?)\s*</think>\s*(.*)", re.DOTALL)


class MessageList(Sequence[ModelMessage]):
    def __init__(self) -> None:
        self._messages: list[ModelMessage] = []

    def get(self) -> list[ModelMessage]:
        return self._messages

    def set(self, new_messages: list[ModelMessage]) -> None:
        self._messages = new_messages

    def strip_think_blocks(self) -> None:
        for msg in self._messages:
            if isinstance(msg, ModelResponse) and len(msg.parts) > 0:
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        _, response_text = self.parse_reasoning(part.content)
                        part.content = response_text or ""

    @staticmethod
    def parse_reasoning(text: str) -> tuple[str | None, str | None]:
        match = think_block_re.search(text)
        if match:
            think_block = match.group(1) or None
            msg = match.group(2).strip() or None
            return think_block, msg
        return None, text.strip() or None

    def __len__(self) -> int:
        return len(self._messages)

    @overload
    def __getitem__(self, index: int) -> ModelMessage: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[ModelMessage]: ...
    def __getitem__(self, index: int | slice) -> ModelMessage | Sequence[ModelMessage]:
        return self._messages[index]
