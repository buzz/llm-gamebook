import math
from time import time
from typing import Final

from rich.style import Style
from rich.text import Text
from textual.app import RenderResult
from textual.color import Color, Gradient
from textual.events import Mount
from textual.widget import Widget


class ThinkingIndicator(Widget, can_focus=False):
    DEFAULT_CSS = """
    ThinkingIndicator {
        height: 1;
    }
    """

    _CHARS: Final = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    _SPEED: Final = 5

    def __init__(self) -> None:
        super().__init__()
        self._start_time: float = 0.0

    def _on_mount(self, _: Mount) -> None:
        self._start_time = time()
        self.auto_refresh = 1 / 10

        color = Color.parse(self.app.theme_variables["text-primary"])
        self._gradient = Gradient(
            (0.0, color.darken(0.2)),
            (1.0, color.lighten(0.2)),
        )

    def render(self) -> RenderResult:
        if self.app.animation_level == "none":
            return Text("Thinking…", no_wrap=True)

        elapsed = time() - self._start_time

        frame = int(elapsed * self._SPEED) % len(self._CHARS)
        current_char = self._CHARS[frame]

        blend = 0.5 * (1 - math.cos(2 * math.pi * (0.1 * elapsed * self._SPEED % 1)))
        style = Style.from_color(self._gradient.get_color(blend).rich_color)

        return Text(f"{current_char} Thinking…", no_wrap=True, style=style)
