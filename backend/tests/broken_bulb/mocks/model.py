from collections import deque
from collections.abc import AsyncIterator, Callable
from inspect import isfunction
from json import dumps
from typing import cast

from pydantic_ai import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelSettings,
    TextPart,
    ToolCallPart,
)
from pydantic_ai.models import ModelRequestParameters
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel

type AssertionLambda = Callable[[list[ModelMessage], AgentInfo], bool]
type MockResponse = ModelResponse | AssertionLambda


class MockModel(FunctionModel):
    """Mock model for testing StoryEngine integration."""

    def __init__(self) -> None:
        super().__init__(stream_function=self._stream_response_function)
        self._response_queue: deque[MockResponse] = deque()
        self._current_messages: list[ModelMessage] = []

    def add_responses(self, *responses: MockResponse) -> None:
        self._response_queue.extend(responses)

    async def _stream_response_function(
        self, messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str | dict[int, DeltaToolCall]]:
        self._current_messages = messages
        mock_response = self._response_queue.popleft()

        # Assertion
        if isfunction(mock_response):
            assertion_lambda = cast("AssertionLambda", mock_response)
            assert assertion_lambda(messages, info)
            mock_response = self._response_queue.popleft()

        assert isinstance(mock_response, ModelResponse)
        for part in mock_response.parts:
            if isinstance(part, TextPart):
                yield part.content
            elif isinstance(part, ToolCallPart):
                yield {
                    0: DeltaToolCall(
                        name=part.tool_name,
                        json_args=dumps(part.args),
                        tool_call_id=part.tool_call_id,
                    )
                }

    @property
    def current_system_prompt(self) -> str:
        # Pydantic AI stores instructions on the most recent ModelRequest
        for msg in reversed(self._current_messages):
            if isinstance(msg, ModelRequest) and msg.instructions is not None:
                return msg.instructions

        err_msg = "No instructions or system prompt found"
        raise ValueError(err_msg)

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        self._current_messages = messages
        return await super().request(messages, model_settings, model_request_parameters)
