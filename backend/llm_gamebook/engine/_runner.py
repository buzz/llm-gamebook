from collections.abc import Sequence
from time import time
from uuid import UUID, uuid4

from pydantic_ai import (
    Agent,
    AgentRun,
    CallToolsNode,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    ModelRequestNode,
    ModelResponse,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
    ToolCallPart,
    ToolCallPartDelta,
)

from llm_gamebook.logger import logger
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import StoryState

from .message import ResponseStreamUpdateMessage


class StreamRunner:
    def __init__(
        self, agent: Agent[StoryState], session_id: UUID, bus: MessageBus, debounce: float
    ) -> None:
        self._agent = agent
        self._session_id = session_id
        self._bus = bus
        self._debounce = debounce

        self._log = logger.getChild(f"stream-runner({session_id})")

        # Generate IDs in advance for key'ing React list nodes
        self._response_index: int = 0
        self._response_ids: list[UUID] = []
        self._part_ids: list[list[UUID]] = []

        self._last_stream_update: float = 0.0
        self._thinking_start_time: float | None = None
        self._thinking_durations: dict[UUID, int] = {}

    async def run(
        self, msg_history: Sequence[ModelMessage], state: StoryState
    ) -> tuple[Sequence[ModelMessage], list[UUID], list[list[UUID]], dict[UUID, int]]:
        messages: list[ModelMessage] = []

        async with self._agent.iter(message_history=msg_history, deps=state) as run:
            async for node in run:
                if Agent.is_model_request_node(node):
                    await self._handle_model_request_node(node, run)
                elif Agent.is_call_tools_node(node):
                    await self._handle_call_tools_node(node, run)
                elif Agent.is_end_node(node):
                    if run.result is None:
                        msg = "Expected result"
                        raise TypeError(msg)
                    messages = run.result.new_messages()
                    if self._thinking_start_time is not None:
                        duration = int(time() - self._thinking_start_time)
                        self._thinking_start_time = None
                        if self._part_ids and self._response_index < len(self._part_ids):
                            response_parts = self._part_ids[self._response_index]
                            if response_parts:
                                last_part_id = response_parts[-1]
                                self._thinking_durations[last_part_id] = duration

        return messages, self._response_ids, self._part_ids, self._thinking_durations

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

            # Force a final update once the stream is exhausted
            await self._send_stream_update(request_stream.response, force=True)

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
            if isinstance(event.part, ThinkingPart):
                self._thinking_start_time = time()
            elif self._thinking_start_time is not None:
                duration = int(time() - self._thinking_start_time)
                self._thinking_start_time = None
                if self._part_ids and self._response_index < len(self._part_ids):
                    response_parts = self._part_ids[self._response_index]
                    if response_parts:
                        last_part_id = response_parts[-1]
                        self._thinking_durations[last_part_id] = duration
            self._log.debug(f"Starting part {event.index}: {event.part!r}")
            self._part_ids[self._response_index].append(uuid4())
            await self._send_stream_update(response)

    async def _handle_part_delta_event(
        self, response: ModelResponse, event: PartDeltaEvent
    ) -> None:
        if isinstance(event.delta, TextPartDelta | ThinkingPartDelta | ToolCallPartDelta):
            await self._send_stream_update(response)

    async def _send_stream_update(self, response: ModelResponse, *, force: bool = False) -> None:
        if force or time() - self._last_stream_update > self._debounce:
            self._bus.publish(
                ResponseStreamUpdateMessage(
                    self._session_id,
                    response,
                    self._response_ids[self._response_index],
                    self._part_ids[self._response_index],
                ),
            )
            self._last_stream_update = time()
