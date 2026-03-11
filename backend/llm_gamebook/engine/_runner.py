from collections.abc import Iterable, Sequence
from time import time
from typing import assert_never
from uuid import UUID

import pydantic_ai as pai

from llm_gamebook.db.models import Message, Part
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.logger import logger
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.context import StoryContext

from .message import (
    ContentDelta,
    Delta,
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
    ToolArgsDelta,
    ToolNameDelta,
)

type Run = pai.AgentRun[StoryContext, str]
type Agent = pai.Agent[StoryContext]
type ModelRequestNode = pai.ModelRequestNode[StoryContext, str]


class _ModelRequestHandler:
    def __init__(self, session_id: UUID, bus: MessageBus, debounce: float) -> None:
        self._session_id = session_id
        self._bus = bus
        self._debounce = debounce

        self._log = logger.getChild(f"stream-runner.model-request-handler({session_id})")

        self._last_delta: float
        self._content: str
        self._content_delta: str
        self._args: str
        self._args_delta: str
        self._tool_name: str
        self._tool_name_delta: str

        self._resp_msg: Message | None = None
        self._part: Part | None = None

    async def handle(self, node: ModelRequestNode, run: Run, context: StoryContext) -> Message:
        req_message = Message.from_model_request(self._session_id, node.request)
        self._bus.publish(StreamMessageMessage(self._session_id, req_message))

        async with node.stream(run.ctx) as req_stream:
            self._resp_msg = Message.from_model_response(self._session_id, req_stream.response)
            self._bus.publish(StreamMessageMessage(self._session_id, self._resp_msg))

            async for event in req_stream:
                self._handle_request_stream(event)

        if not context.session_state.is_empty():
            self._resp_msg.state = context.session_state.data.model_dump()

        return self._resp_msg

    def _handle_request_stream(self, event: pai.ModelResponseStreamEvent) -> None:
        if isinstance(event, pai.PartStartEvent):
            self._log.debug("%s", event)
            self._handle_part_start_event(event)

        elif isinstance(event, pai.PartDeltaEvent):
            # self._log.debug("%s", event)
            self._handle_part_delta_event(event)

        elif isinstance(event, pai.PartEndEvent):
            self._log.debug("%s", event)
            self._handle_part_end_event(event)

        elif isinstance(event, pai.FinalResultEvent):
            self._log.debug("%s", event)

        else:
            assert_never(event)

    def _handle_part_start_event(self, event: pai.PartStartEvent) -> None:
        self._reset_part()
        assert self._resp_msg

        if isinstance(event.part, pai.TextPart | pai.ThinkingPart | pai.ToolCallPart):
            if isinstance(event.part, pai.TextPart | pai.ThinkingPart):
                self._content += event.part.content

            elif isinstance(event.part, pai.ToolCallPart):
                if isinstance(event.part.args, str):
                    self._args += event.part.args
                self._tool_name = event.part.tool_name

            self._part = Part.from_model_response_part(event.part)
            self._part.message = self._resp_msg
            self._part.message_id = self._resp_msg.id
            self._bus.publish(StreamPartMessage(self._session_id, self._resp_msg.id, self._part))
            self._last_delta = time()

    def _handle_part_delta_event(self, event: pai.PartDeltaEvent) -> None:
        assert self._resp_msg is not None
        assert self._part is not None

        if isinstance(event.delta, pai.TextPartDelta):
            self._content_delta += event.delta.content_delta

        if isinstance(event.delta, pai.ThinkingPartDelta):
            self._content_delta += event.delta.content_delta or ""

        elif isinstance(event.delta, pai.ToolCallPartDelta):
            if isinstance(event.delta.args_delta, str):
                self._args_delta += event.delta.args_delta

            if isinstance(event.delta.tool_name_delta, str):
                self._tool_name_delta += event.delta.tool_name_delta

        now = time()
        if now - self._last_delta > self._debounce:
            self._drain_delta(event.delta)
            self._publish_delta()
            self._last_delta = now

    def _handle_part_end_event(self, event: pai.PartEndEvent) -> None:
        assert self._resp_msg is not None
        assert self._part is not None

        if isinstance(event.part, pai.TextPart | pai.ThinkingPart | pai.ToolCallPart):
            if isinstance(event.part, pai.TextPart):
                self._content += self._content_delta
                self._part.content = self._content

            elif isinstance(event.part, pai.ThinkingPart):
                self._content += self._content_delta
                self._part.content = self._content
                self._part.duration_seconds = int(time() - self._part.timestamp.timestamp())

            elif isinstance(event.part, pai.ToolCallPart):
                self._args += self._args_delta
                self._part.args = self._args
                self._tool_name += self._tool_name_delta
                self._part.tool_name = self._tool_name

            self._resp_msg.parts.append(self._part)

            # Make sure last delta is sent
            self._publish_delta()

    def _drain_delta(self, event_delta: pai.ModelResponsePartDelta) -> None:
        if isinstance(event_delta, pai.TextPartDelta | pai.ThinkingPartDelta):
            self._content += self._content_delta

        elif isinstance(event_delta, pai.ToolCallPartDelta):
            if self._args_delta:
                self._args += self._args_delta
            elif self._tool_name_delta:
                self._tool_name += self._tool_name_delta

    def _publish_delta(self) -> None:
        assert self._resp_msg is not None
        assert self._part is not None

        delta: Delta | None = None
        if self._part.kind in {PartKind.TEXT, PartKind.THINKING} and self._content_delta:
            delta = ContentDelta(self._content_delta)
            self._content_delta = ""

        elif self._part.kind == PartKind.TOOL_CALL:
            if self._args_delta:
                delta = ToolArgsDelta(self._args_delta)
                self._args_delta = ""
            elif self._tool_name_delta:
                delta = ToolNameDelta(self._tool_name_delta)
                self._tool_name_delta = ""

        if delta:
            delta_msg = StreamPartDeltaMessage(
                self._session_id,
                self._resp_msg.id,
                self._part.id,
                delta,
            )
            self._bus.publish(delta_msg)

    def reset(self) -> None:
        self._reset_part()
        self._resp_msg = None

    def _reset_part(self) -> None:
        self._part = None
        self._last_delta = 0.0
        self._content = ""
        self._content_delta = ""
        self._args = ""
        self._args_delta = ""
        self._tool_name = ""
        self._tool_name_delta = ""


class StreamRunner:
    def __init__(self, agent: Agent, session_id: UUID, bus: MessageBus, debounce: float) -> None:
        self._agent = agent
        self._session_id = session_id
        self._bus = bus
        self._debounce = debounce

        self._messages: list[Message] = []

        self._log = logger.getChild(f"stream-runner({session_id})")

    async def run(
        self, msg_history: Sequence[pai.ModelMessage], context: StoryContext
    ) -> Iterable[Message]:
        handler = _ModelRequestHandler(self._session_id, self._bus, self._debounce)

        # Run agent
        async with self._agent.iter(message_history=msg_history, deps=context) as run:
            async for node in run:
                if pai.Agent.is_user_prompt_node(node):
                    self._log.debug("UserPromptNode: %s", node.user_prompt)

                elif pai.Agent.is_model_request_node(node):
                    self._log.debug("ModelRequestNode: %s", node.request)
                    handler.reset()
                    message = await handler.handle(node, run, context)
                    self._messages.append(message)

                elif pai.Agent.is_call_tools_node(node):
                    self._log.debug("CallToolsNode: %s", node.model_response)
                    await self._handle_call_tools_node(node, run)

                elif pai.Agent.is_end_node(node):
                    self._log.debug("End: %s", run.result)
                    break

        # Store messages
        return self._messages

    async def _handle_call_tools_node(
        self, node: pai.CallToolsNode[StoryContext, str], run: Run
    ) -> None:
        # A handle-response node => The model returned some data, potentially calls a tool
        async with node.stream(run.ctx) as handle_stream:
            async for event in handle_stream:
                if isinstance(event, pai.FunctionToolCallEvent):
                    # Handled as part in _handle_model_request_node
                    self._log.debug(
                        "[Tools] The LLM calls tool=%s with args=%s (tool_call_id=%s)",
                        event.part.tool_name,
                        event.part.args,
                        event.part.tool_call_id,
                    )

                elif isinstance(event, pai.FunctionToolResultEvent):
                    self._log.debug(
                        "[Tools] Tool call %s returned => %s",
                        event.tool_call_id,
                        event.result.content,
                    )
