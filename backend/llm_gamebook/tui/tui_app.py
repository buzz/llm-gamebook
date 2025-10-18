from collections.abc import Callable
from typing import Any, ClassVar

from pydantic_ai.messages import ModelMessage
from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer

from llm_gamebook.constants import PROJECT_NAME
from llm_gamebook.engine.engine import StreamState
from llm_gamebook.logger import logger
from llm_gamebook.tui.message_list import MessageList
from llm_gamebook.tui.user_input import UserInput


class Header(Widget, can_focus=False):
    def render(self) -> RenderResult:
        return f"📖 [b]{PROJECT_NAME}[/b]"


log = logger.getChild("tui")


class TuiApp(App):
    TITLE = PROJECT_NAME
    CSS_PATH: ClassVar = ["tui_app.tcss", "message_list.tcss"]

    BINDINGS: ClassVar = [
        Binding(key="ctrl+u", action="show_internals", description="Show internals"),
        Binding(key="ctrl+h", action="help", description="Help", priority=True),
        Binding(key="ctrl+q", action="quit", description="Quit", priority=True),
    ]
    ENABLE_COMMAND_PALETTE = False

    show_internals: reactive[bool] = reactive(default=True)

    def __init__(self, *args: Any, debug: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._debug = debug
        self._shutdown_callable: Callable[[], None] | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield MessageList().data_bind(TuiApp.show_internals)
            yield UserInput()
        yield Footer()

    # --- Actions

    async def action_quit(self) -> None:
        if self._shutdown_callable:
            self._shutdown_callable()
        await super().action_quit()

    def action_help(self) -> None:
        # TODO: help screen
        pass

    def action_show_internals(self) -> None:
        self.show_internals = not self.show_internals

    # --- Event handlers

    def on_tui_app_messages_updated(self, message: "TuiApp.MessagesUpdated") -> None:
        self.query_one(MessageList).messages = message.messages

    def on_tui_app_stream_state_updated(self, message: "TuiApp.StreamStateUpdated") -> None:
        self.query_one(MessageList).stream_state_update(message)

    # --- Events

    class MessagesUpdated(Message):
        def __init__(self, messages: list[ModelMessage]) -> None:
            super().__init__()
            self.messages = messages

    class StreamStateUpdated(Message):
        def __init__(self, state: StreamState, text: str | None) -> None:
            super().__init__()
            self.state = state
            self.text = text

    # --- UserInterface protocol

    def messages_update(self, messages: list[ModelMessage]) -> None:
        self.post_message(self.MessagesUpdated(messages))

    def stream_state_update(self, state: StreamState, text: str | None = None) -> None:
        self.post_message(self.StreamStateUpdated(state, text))

    async def get_user_input(self) -> str:
        return await self.query_one(UserInput).wait_for_input()

    def set_shutdown_callable(self, func: Callable[[], None]) -> None:
        self._shutdown_callable = func

    def shutdown(self) -> None:
        self.exit()
