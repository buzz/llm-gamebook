import random
from collections.abc import Sequence
from uuid import UUID, uuid4

from pydantic_ai import Agent, ModelResponse, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.engine.messages import MessageList
from llm_gamebook.logger import logger
from llm_gamebook.story.state import StoryState


class StoryEngine:
    def __init__(
        self,
        chat_id: UUID,
        model: Model,
        state: StoryState,
        *,
        streaming: bool = True,
    ) -> None:
        self._log = logger.getChild("engine")

        self._chat_id = chat_id
        self._state = state
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

    async def generate_llm_message(self) -> tuple[UUID, ModelResponse]:
        self._log.info("generate_llm_message called")

        while True:
            new_messages = await self._agent_run()
            self._messages.append(new_messages)

            # Get user message
            if not self._messages.last_message_was_tool_return:
                new_message = new_messages[-1]
                if isinstance(new_message, ModelResponse):
                    return uuid4(), new_message
                break

        msg = "No LLM response"
        raise RuntimeError(msg)

    async def _agent_run(self) -> Sequence[ModelMessage]:
        msg_hist = await self._messages.get_messages(for_llm=True)

        if self._streaming:
            async with self._agent.run_stream(
                message_history=msg_hist, deps=self._state
            ) as streamed_result:
                # with self._stream_printer() as handle:
                #     async for message in streamed_result.stream_text(delta=True):
                #         handle(message)
                pass
            return streamed_result.new_messages()

        # non-streaming
        result = await self._agent.run(message_history=msg_hist, deps=self._state)
        return result.new_messages()

    async def _prepare_tools(
        self,
        ctx: RunContext[StoryState],
        tools: list[ToolDefinition],
    ) -> list[ToolDefinition] | None:
        # No tools for introduction message
        return tools if len(ctx.messages) > 2 else None
