import asyncio
import logging
import random
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from enum import Enum, auto
from typing import TYPE_CHECKING, Final

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.engine.messages import MessageList
from llm_gamebook.logger import logger
from llm_gamebook.story.state import StoryState

if TYPE_CHECKING:
    from llm_gamebook.types import UserInterface


class StreamState(Enum):
    INIT = auto()
    THINK = auto()
    RESPONSE = auto()
    INACTIVE = auto()


class StoryEngine:
    _start_tag: Final = "<think>"
    _end_tag: Final = "</think>"

    def __init__(
        self, model: Model, state: StoryState, ui: "UserInterface", *, streaming: bool = True
    ) -> None:
        self._log = logger.getChild("engine")
        self._state = state
        self._ui = ui
        self._streaming = streaming
        self._messages = MessageList(self._state)
        self._agent = Agent[StoryState, str](
            model,
            deps_type=StoryState,
            model_settings=ModelSettings(seed=random.randint(0, 10000), temperature=0.8),
            output_type=str,
            tools=list(self._state.get_tools()),
            prepare_tools=self._prepare_tools,
        )
        self._run_task: asyncio.Task | None = None

        self._ui.set_shutdown_callable(self._ui_shutdown)

    async def run(self) -> None:
        self._run_task = asyncio.create_task(self._run())
        await self._run_task

    async def _run(self) -> None:
        try:
            user_input: str | None = None

            while True:
                await self._ui_messages_update()

                # Run agent
                new_messages = await self._agent_run()
                self._messages.append(new_messages)
                await self._ui_messages_update()

                # Get user message
                if self._messages.last_message_was_tool_return:
                    user_input = None
                else:
                    user_input = await self._ui.get_user_input()
                    self._messages.append_user_prompt(user_input)

        except asyncio.CancelledError:
            pass
        finally:
            self._ui.shutdown()

    async def _agent_run(self) -> Sequence[ModelMessage]:
        msg_hist = await self._messages.get_messages(for_llm=True)

        if self._streaming:
            async with self._agent.run_stream(
                message_history=msg_hist, deps=self._state
            ) as streamed_result:
                with self._stream_printer() as handle:
                    async for message in streamed_result.stream_text(delta=True):
                        handle(message)
            return streamed_result.new_messages()

        # non-streaming
        result = await self._agent.run(message_history=msg_hist, deps=self._state)
        return result.new_messages()

    @contextmanager
    def _stream_printer(self) -> Iterator[Callable[[str], None]]:
        buffer = ""
        state: StreamState

        def handle(chunk: str) -> None:
            nonlocal buffer, state
            buffer += chunk
            while True:
                if state == StreamState.INIT:
                    if len(buffer) < len(self._start_tag):
                        return
                    if buffer.startswith(self._start_tag):
                        buffer = buffer[len(self._start_tag) :].lstrip()
                        state = StreamState.THINK
                    else:
                        state = StreamState.RESPONSE

                elif state == StreamState.THINK:
                    idx = buffer.find(self._end_tag)
                    if idx == -1:
                        keep = max(0, len(buffer) - len(self._end_tag))
                        self._ui.stream_state_update(state, buffer[:keep])
                        buffer = buffer[keep:]
                        return
                    self._ui.stream_state_update(state, buffer[:idx].rstrip())
                    buffer = buffer[idx + len(self._end_tag) :].lstrip()
                    state = StreamState.RESPONSE

                elif state == StreamState.RESPONSE:
                    self._ui.stream_state_update(state, buffer)
                    buffer = ""
                    return

        try:
            state = StreamState.INIT
            self._ui.stream_state_update(state)
            yield handle
        finally:
            state = StreamState.INACTIVE
            self._ui.stream_state_update(state)

    async def _prepare_tools(
        self,
        ctx: RunContext[StoryState],
        tools: list[ToolDefinition],
    ) -> list[ToolDefinition] | None:
        # No tools for introductory message
        return tools if len(ctx.messages) > 2 else None

    async def _ui_messages_update(self) -> None:
        ui_messages = await self._messages.get_messages(for_llm=False)
        self._ui.messages_update(ui_messages)

    def _ui_shutdown(self) -> None:
        if self._run_task and not self._run_task.done():
            self._run_task.cancel()

    @property
    def _is_debug(self) -> bool:
        return self._log.getEffectiveLevel() == logging.DEBUG
