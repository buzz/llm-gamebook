import re
from time import time
from typing import TYPE_CHECKING, Final

from pydantic_ai.messages import (
    ModelMessage,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView
from textual.widgets import Markdown as TextualMarkdown

from llm_gamebook.engine.engine import StreamState
from llm_gamebook.tui.thinking_indicator import ThinkingIndicator

if TYPE_CHECKING:
    from llm_gamebook.tui.tui_app import TuiApp

think_block_re = re.compile(r"<think>\s*(.*?)\s*</think>\s*(.*)", re.DOTALL)


def parse_reasoning(text: str) -> tuple[str | None, str | None]:
    match = think_block_re.search(text)
    if match:
        think_block = match.group(1) or None
        msg = match.group(2).strip() or None
        return think_block, msg
    return None, text.strip() or None


class Markdown(Widget):
    text: reactive[str] = reactive("", layout=True, recompose=True)

    def __init__(self, text: str = "", classes: str | None = None) -> None:
        super().__init__()
        self.text = text
        self._md_classes = classes

    def compose(self) -> ComposeResult:
        yield TextualMarkdown(self.text, open_links=False, classes=self._md_classes)


class ThinkBlock(VerticalGroup):
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        yield Label("<think>", expand=True, markup=False, classes="dim")
        yield Markdown(self.text, classes="think")
        yield Label("</think>", expand=True, markup=False, classes="dim")


class MessageItem(ListItem):
    def __init__(self, message: ModelMessage, *, show_internals: bool) -> None:
        super().__init__()
        self.message = message
        self.show_internals = show_internals

    def compose(self) -> ComposeResult:
        for part in self.message.parts:
            if isinstance(part, TextPart):
                with VerticalGroup():
                    think_text, response_text = parse_reasoning(part.content)
                    if think_text and self.show_internals:
                        yield ThinkBlock(think_text)
                    if response_text:
                        yield Markdown(response_text, classes="assistant")

            elif isinstance(part, UserPromptPart):
                if isinstance(part.content, str):
                    yield HorizontalGroup(
                        Label(">", markup=False, classes="user_prompt"),
                        Markdown(part.content, classes="user"),
                    )

            elif self.show_internals:
                if isinstance(part, SystemPromptPart):
                    yield Markdown(part.content, classes="system")

                elif isinstance(part, ToolCallPart):
                    label = f"Tool Call: {part.tool_name} Args: {part.args_as_json_str()}"
                    yield Label(label, classes="tool", markup=False, expand=True)

                elif isinstance(part, ToolReturnPart):
                    label = f"Tool Return: {part.tool_name} Args: {part.model_response_str()}"
                    yield Label(label, classes="tool", markup=False, expand=True)

                else:
                    label = f"Unknown part: {type(part).__name__}"
                    yield Label(label, classes="unknown", markup=False, expand=True)


class StreamDisplay(ListItem):
    _DEBOUNCE_INTERVAL: Final = 0.1

    show_internals: reactive[bool] = reactive(default=False)

    def __init__(self, *, show_internals: bool) -> None:
        super().__init__()
        self.show_internals = show_internals
        self._last_update: float = 0.0
        self._think_text: str = ""
        self._response_text: str = ""

        self._indicator = ThinkingIndicator()
        self._think_block = ThinkBlock("")
        self._response_block = Markdown("", classes="assistant")

        self._indicator.display = False
        self._think_block.display = False
        self._response_block.display = False

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield self._indicator
            yield self._think_block
            yield self._response_block

    def update(self, message: "TuiApp.StreamStateUpdated") -> None:
        if message.text:
            if message.state == StreamState.THINK:
                self._think_text += message.text
            elif message.state == StreamState.RESPONSE:
                self._response_text += message.text

            if time() - self._last_update > self._DEBOUNCE_INTERVAL:
                self._debounced_update()

    def _debounced_update(self) -> None:
        self._indicator.display = not self.show_internals and len(self._response_text) == 0

        if self.show_internals and len(self._think_text) > 0:
            self._think_block.display = True
            if self._think_block.text != self._think_text:
                self._think_block.text = self._think_text
                self._think_block.refresh(recompose=True)
        else:
            self._think_block.display = False

        if len(self._response_text) > 0:
            self._response_block.display = True
            if self._response_block.text != self._response_text:
                self._response_block.text = self._response_text
                self._response_block.refresh(recompose=True)

        self.post_message(StreamDisplay.Updated())
        self._last_update = time()

    class Updated(Message):
        pass


class MessageList(ListView):
    messages: reactive[list[ModelMessage]] = reactive([], recompose=True)
    show_internals: reactive[bool] = reactive(default=False, recompose=True)

    def __init__(self) -> None:
        self._stream_display: StreamDisplay | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        for idx, message in enumerate(self.messages):
            if self._should_show_message(idx, message):
                yield MessageItem(message, show_internals=self.show_internals)

    def stream_state_update(self, message: "TuiApp.StreamStateUpdated") -> None:
        if message.state == StreamState.INIT:
            self._stream_display = StreamDisplay(show_internals=self.show_internals)
            self.mount(self._stream_display)
        elif self._stream_display:
            if message.text:
                self._stream_display.update(message)
            elif message.state == StreamState.INACTIVE:
                self._stream_display.remove()
                self._stream_display = None

    # --- Watchers

    def watch_show_internals(self, _: bool, show_internals: bool) -> None:  # noqa: FBT001
        # Data binding doesn't appear to work with dynamically created widgets
        if self._stream_display:
            self._stream_display.show_internals = show_internals

    def watch_messages(self, _: list[ModelMessage], messages: list[ModelMessage]) -> None:
        self._scroll_end()

    # --- Event handlers

    def on_stream_display_updated(self, message: StreamDisplay.Updated) -> None:
        self._scroll_end()

    # --- Helpers

    def _scroll_end(self) -> None:
        self.scroll_end(animate=False, x_axis=False)

    def _should_show_message(self, index: int, message: ModelMessage) -> bool:
        # Skip introductory message
        if index == 0 and not self.show_internals:
            return False

        relevant = (
            (
                TextPart,
                UserPromptPart,
                SystemPromptPart,
                ToolCallPart,
                ToolReturnPart,
            )
            if self.show_internals
            else (TextPart, UserPromptPart)
        )
        return any(p for p in message.parts if isinstance(p, relevant))
