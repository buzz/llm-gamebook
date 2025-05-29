import re
import unicodedata
from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBusMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._event_subscribers: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[..., None]) -> None:
        self._event_subscribers[event_type].append(handler)

    def emit(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        for handler in self._event_subscribers[event_type]:
            handler(*args, **kwargs)


def slugify(text: str) -> str:
    # Normalize and remove accents
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
