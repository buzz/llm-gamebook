import asyncio
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import Key
from textual.message import Message
from textual.widgets import Label, TextArea


class UserInputTextArea(TextArea):
    def __init__(self, submit_event: asyncio.Event) -> None:
        super().__init__(compact=True, disabled=True)
        self.cursor_blink = False
        self.styles.height = 3
        self._submit_event = submit_event

    def _check_height(self) -> None:
        height = self.wrapped_document.height
        self.post_message(self.HeightChanged(height))

    # --- Actions

    def action_insert_newline(self) -> None:
        start, end = self.selection
        self._replace_via_keyboard("\n", start, end)

    # --- Event handlers

    def on_mount(self) -> None:
        super().on_mount()
        self._check_height()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._check_height()

    def on_user_input_text_area_height_changed(
        self, message: "UserInputTextArea.HeightChanged"
    ) -> None:
        self.styles.height = message.height

    async def _on_key(self, event: Key) -> None:
        if event.key == "enter":
            if self.text:
                self._submit_event.set()
            event.prevent_default()

    # --- Events

    class HeightChanged(Message):
        def __init__(self, height: int) -> None:
            super().__init__()
            self.height = height


class UserInput(Horizontal):
    BINDINGS: ClassVar = [
        Binding(key="ctrl+j", action="insert_newline", description="Insert newline"),
        Binding(key="ctrl+u", action="show_internals", description="Show internals"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._submit_event = asyncio.Event()

    def compose(self) -> ComposeResult:
        yield Label(">", markup=False)
        yield UserInputTextArea(self._submit_event)

    async def wait_for_input(self) -> str:
        text_area = self.query_one(UserInputTextArea)
        self._submit_event.clear()
        text_area.disabled = False
        text_area.focus()
        await self._submit_event.wait()
        text = text_area.text
        text_area.disabled = True
        text_area.clear()
        return text

    # --- Actions

    def action_insert_newline(self) -> None:
        text_area = self.query_one(UserInputTextArea)
        start, end = text_area.selection
        text_area.replace("\n", start, end, maintain_selection_offset=False)

    # --- Event handlers

    def on_user_input_text_area_height_changed(
        self, message: UserInputTextArea.HeightChanged
    ) -> None:
        height = message.height + 1
        height = max(height, 2)
        height = min(height, self.app.size.height // 2)
        self.styles.height = height
