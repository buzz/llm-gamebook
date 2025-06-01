import unicodedata
from collections import defaultdict
from collections.abc import Callable
from typing import Any

import casefy


class EventBusMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._event_subscribers: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[..., None]) -> None:
        self._event_subscribers[event_type].append(handler)

    def emit(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        for handler in self._event_subscribers[event_type]:
            handler(*args, **kwargs)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def normalized_snake_case(text: str) -> str:
    return casefy.snakecase(normalize(text))


def normalized_pascal_case(text: str) -> str:
    return casefy.pascalcase(normalize(text))
