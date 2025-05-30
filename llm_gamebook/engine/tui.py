# ruff: noqa: T201 (allow print)
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Final

from colorama import Fore, Style


class TextUserInterface:
    _start_tag: Final = "<think>"
    _end_tag: Final = "</think>"

    def __init__(self, *, debug: bool = False) -> None:
        self._debug = debug

    def text_response(self, think_text: str | None, text: str | None) -> None:
        if self._debug and think_text:
            print(f"\n<think>\n{Style.DIM}{think_text}{Style.RESET_ALL}\n</think>")
        if text:
            print(f"\n{Style.BRIGHT}{text}{Style.RESET_ALL}")

    def tool_call(self, tool_name: str, tool_args: str) -> None:
        print(f"\n{Fore.YELLOW}Tool call: {tool_name}({tool_args}){Fore.RESET}\n")

    @contextmanager
    def stream_printer(self) -> Iterator[Callable[[str], None]]:
        buffer = ""
        state = "INIT"  # INIT, THINK, NORMAL

        def flush_think(text: str) -> None:
            if self._debug:
                print(f"{Style.DIM}{text}{Style.RESET_ALL}", end="", flush=True)

        def flush_normal(text: str) -> None:
            print(f"{Style.BRIGHT}{text}{Style.RESET_ALL}", end="", flush=True)

        def handle(chunk: str) -> None:
            nonlocal buffer, state
            buffer += chunk
            while True:
                if state == "INIT":
                    if len(buffer) < len(self._start_tag):
                        return
                    if buffer.startswith(self._start_tag):
                        buffer = buffer[len(self._start_tag) :].lstrip()
                        state = "THINK"
                    else:
                        state = "NORMAL"
                elif state == "THINK":
                    idx = buffer.find(self._end_tag)
                    if idx == -1:
                        keep = max(0, len(buffer) - len(self._end_tag))
                        flush_think(buffer[:keep])
                        buffer = buffer[keep:]
                        return
                    flush_think(f"{buffer[:idx].rstrip()}\n\n")
                    buffer = buffer[idx + len(self._end_tag) :].lstrip()
                    state = "NORMAL"
                elif state == "NORMAL":
                    flush_normal(buffer)
                    buffer = ""
                    return

        try:
            yield handle
        finally:
            print(flush=True)

    async def get_user_input(self) -> str:
        return input("\n> ")
