from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseMessage:
    pass


type MessageHandler[T: BaseMessage] = Callable[[T], Awaitable[None] | None]
