import random
from collections.abc import Sequence
from time import time
from typing import Final, TypedDict
from uuid import UUID, uuid4

import httpx
from openai import OpenAIError
from pydantic_ai import (
    Agent,
    AgentRun,
    AgentRunError,
    CallToolsNode,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    ModelRequestNode,
    ModelResponse,
    PartDeltaEvent,
    PartStartEvent,
    RunContext,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
    ToolCallPart,
    ToolCallPartDelta,
    UsageLimits,
)
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.tools import ToolDefinition
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.logger import logger
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import StoryState

from .session_adapter import SessionAdapter


class StoryEngine:
    def __init__(self, session_id: UUID, model: Model, state: StoryState, bus: MessageBus) -> None:
        self._state = state
        self._session_adapter = SessionAdapter(session_id, state, bus)
        self._bus = bus
        self._log = logger.getChild(f"engine-{session_id}")
        self._agent = Agent[StoryState, str](
            model,
            deps_type=StoryState,
            model_settings=ModelSettings(seed=random.randint(0, 10000), temperature=0.8),
            output_type=str,
            tools=list(self._state.get_tools()),
            prepare_tools=self._prepare_tools,
        )

    async def generate_response(
        self, db_session: AsyncDbSession, *, streaming: bool = False
    ) -> None:
        self._log.info("Generating new response")
        self._bus.publish("engine.response.started", self._session_adapter.session_id)
        try:
            msg_history = await self._session_adapter.get_message_history(db_session)
            if streaming:
                runner = _StreamRunner(self._agent, self._session_adapter.session_id, self._bus)
                new_messages, message_ids, parts_ids = await runner.run(msg_history, self._state)
                await self._session_adapter.append_messages(
                    db_session, new_messages, message_ids, parts_ids
                )
            else:
                result = await self._agent.run(message_history=msg_history, deps=self._state)
                new_messages = result.new_messages()
                await self._session_adapter.append_messages(db_session, new_messages)
        except (httpx.RequestError, OpenAIError, AgentRunError) as err:
            self._log.exception("Request failed. The exception was:")
            self._bus.publish(
                "engine.response.error",
                ResponseErrorBusMessage(session_id=self._session_adapter.session_id, error=err),
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


class _StreamRunner:
    _DEBOUNCE: Final[float] = 0.1  # secs

    def __init__(
        self,
        agent: Agent[StoryState],
        session_id: UUID,
        bus: MessageBus,
    ) -> None:
        self._agent = agent
        self._session_id = session_id
        self._bus = bus

        self._log = logger.getChild(f"stream-runner({session_id})")

        # Generate IDs in advance for key'ing React list nodes
        self._response_index: int = 0
        self._response_ids: list[UUID] = []
        self._part_ids: list[list[UUID]] = []

        self._last_stream_update: float = 0.0

    async def run(
        self, msg_history: Sequence[ModelMessage], state: StoryState
    ) -> tuple[Sequence[ModelMessage], list[UUID], list[list[UUID]]]:
        messages: list[ModelMessage] = []

        async with self._agent.iter(
            message_history=msg_history,
            deps=state,
            usage_limits=UsageLimits(output_tokens_limit=200_000),
        ) as run:
            async for node in run:
                if Agent.is_model_request_node(node):
                    await self._handle_model_request_node(node, run)
                elif Agent.is_call_tools_node(node):
                    await self._handle_call_tools_node(node, run)
                elif Agent.is_end_node(node):
                    # Once an End node is reached, the agent run is complete
                    if run.result is None:
                        msg = "Expected result"
                        raise TypeError(msg)
                    messages = run.result.new_messages()

        return messages, self._response_ids, self._part_ids

    async def _handle_model_request_node(
        self, node: ModelRequestNode[StoryState, str], run: AgentRun[StoryState, str]
    ) -> None:
        self._log.debug("ModelRequestNode: streaming partial request tokens")
        async with node.stream(run.ctx) as request_stream:
            self._response_ids.append(uuid4())
            self._part_ids.append([])
            async for event in request_stream:
                if isinstance(event, PartStartEvent):
                    await self._handle_part_start_event(request_stream.response, event)
                elif isinstance(event, PartDeltaEvent):
                    await self._handle_part_delta_event(request_stream.response, event)
            self._response_index += 1

    async def _handle_call_tools_node(
        self, node: CallToolsNode[StoryState, str], run: AgentRun[StoryState, str]
    ) -> None:
        # A handle-response node => The model returned some data, potentially calls a tool
        self._log.debug("CallToolsNode: streaming partial response & tool usage")
        async with node.stream(run.ctx) as handle_stream:
            async for event in handle_stream:
                # TODO: how to handle tools?
                if isinstance(event, FunctionToolCallEvent):
                    self._log.debug(
                        "[Tools] The LLM calls tool=%s with args=%s (tool_call_id=%s)",
                        event.part.tool_name,
                        event.part.args,
                        event.part.tool_call_id,
                    )
                elif isinstance(event, FunctionToolResultEvent):
                    self._log.debug(
                        "[Tools] Tool call %s returned => %s",
                        event.tool_call_id,
                        event.result.content,
                    )

    async def _handle_part_start_event(
        self, response: ModelResponse, event: PartStartEvent
    ) -> None:
        if isinstance(event.part, TextPart | ThinkingPart | ToolCallPart):
            self._log.debug(f"Starting part {event.index}: {event.part!r}")
            self._part_ids[self._response_index].append(uuid4())
            await self._send_stream_update(response)

    async def _handle_part_delta_event(
        self, response: ModelResponse, event: PartDeltaEvent
    ) -> None:
        if isinstance(event.delta, TextPartDelta | ThinkingPartDelta | ToolCallPartDelta):
            await self._send_stream_update(response)

    async def _send_stream_update(self, response: ModelResponse) -> None:
        if time() - self._last_stream_update > self._DEBOUNCE:
            self._bus.publish(
                "engine.response.stream",
                StreamUpdateBusMessage(
                    session_id=self._session_id,
                    response=response,
                    response_id=self._response_ids[self._response_index],
                    part_ids=self._part_ids[self._response_index],
                ),
            )
            self._last_stream_update = time()


class StreamUpdateBusMessage(TypedDict):
    session_id: UUID
    response: ModelResponse
    response_id: UUID
    part_ids: list[UUID]


class ResponseErrorBusMessage(TypedDict):
    session_id: UUID
    error: Exception
