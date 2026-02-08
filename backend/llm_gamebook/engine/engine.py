import logging
import random
from collections.abc import Sequence
from contextlib import suppress
from uuid import UUID

import httpx
from openai import OpenAIError
from pydantic_ai import (
    Agent,
    AgentRunError,
    ModelAPIError,
    ModelHTTPError,
    ModelMessage,
    RunContext,
)
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import ToolDefinition
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.logger import logger
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import StoryState

from ._runner import StreamRunner
from .message import ResponseErrorBusMessage
from .session_adapter import SessionAdapter


class StoryEngine:
    def __init__(
        self,
        session_id: UUID,
        model: Model,
        state: StoryState,
        bus: MessageBus,
        stream_debounce: float = 0.1,
    ) -> None:
        self._state = state
        self._session_adapter = SessionAdapter(session_id, state, bus)
        self._bus = bus
        self._log = logger.getChild(f"engine-{session_id}")
        self._stream_debounce = stream_debounce
        self.set_model(model)

    async def generate_response(
        self, db_session: AsyncDbSession, *, streaming: bool = False
    ) -> None:
        self._log.info("Generating new response")
        self._bus.publish("engine.response.started", self._session_adapter.session_id)
        try:
            msg_history = [
                msg async for msg in self._session_adapter.get_message_history(db_session)
            ]

            if self._log.level <= logging.DEBUG:
                self._log_messages(msg_history)

            # Streaming run
            if streaming:
                runner = StreamRunner(
                    self._agent, self._session_adapter.session_id, self._bus, self._stream_debounce
                )
                streaming_result = await runner.run(msg_history, self._state)
                new_messages, message_ids, parts_ids, durations = streaming_result
                await self._session_adapter.append_messages(
                    db_session, new_messages, message_ids, parts_ids, durations
                )

            # Non-streaming run
            else:
                result = await self._agent.run(message_history=msg_history, deps=self._state)
                new_messages = result.new_messages()
                await self._session_adapter.append_messages(db_session, new_messages)

        except (httpx.RequestError, OpenAIError, AgentRunError, ModelAPIError) as err:
            self._log.exception("Request failed. The exception was:")
            if isinstance(err, ModelHTTPError):
                if isinstance(err.body, dict):
                    with suppress(KeyError):
                        message = err.body["message"]
                self._log.error("The error message:\n%s", message)
            self._bus.publish(
                "engine.response.error",
                ResponseErrorBusMessage(self._session_adapter.session_id, err),
            )
        finally:
            self._bus.publish("engine.response.stopped", self._session_adapter.session_id)

    async def _prepare_tools(
        self,
        ctx: RunContext[StoryState],
        tools: list[ToolDefinition],
    ) -> list[ToolDefinition] | None:
        # No tools for introduction message
        return tools if len(ctx.messages) > 2 else None

    @property
    def session_adapter(self) -> SessionAdapter:
        return self._session_adapter

    def set_model(self, model: Model) -> None:
        self._agent = Agent[StoryState, str](
            model,
            deps_type=StoryState,
            model_settings=ModelSettings(seed=random.randint(0, 10000), temperature=0.8),
            output_type=str,
            tools=list(self._state.get_tools()),
            prepare_tools=self._prepare_tools,
        )

    def _log_messages(self, messages: Sequence[ModelMessage]) -> None:
        for idx, msg in enumerate(messages):
            self._log.debug("%03d: %s", idx, type(msg).__name__)
            for pidx, part in enumerate(msg.parts):
                content = part.content if hasattr(part, "content") else "- NO CONTENT -"
                self._log.debug("   %03d: %-20s %.250s", pidx, type(part).__name__, content)
