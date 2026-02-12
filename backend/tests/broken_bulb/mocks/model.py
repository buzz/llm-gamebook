from collections import deque
from collections.abc import Callable
from inspect import isfunction
from typing import cast

from pydantic_ai import ModelMessage, ModelRequest, ModelResponse, ModelSettings
from pydantic_ai.models import ModelRequestParameters
from pydantic_ai.models.function import AgentInfo, FunctionModel

type AssertionLambda = Callable[[list[ModelMessage], AgentInfo], bool]
type MockResponse = ModelResponse | AssertionLambda


class MockModel(FunctionModel):
    """Mock model for testing StoryEngine integration."""

    def __init__(self) -> None:
        super().__init__(self._response_function)
        self._response_queue: deque[MockResponse] = deque()
        self._current_messages: list[ModelMessage] = []

    def add_responses(self, *responses: MockResponse) -> None:
        self._response_queue.extend(responses)

    def _response_function(self, messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        while mock_response := self._response_queue.popleft():
            # Assertion
            if isfunction(mock_response):
                assertion_lambda = cast("AssertionLambda", mock_response)
                assert assertion_lambda(messages, info)
            else:
                assert isinstance(mock_response, ModelResponse)
                return mock_response

        msg = "No ModelResponse was added"
        raise ValueError(msg)

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
