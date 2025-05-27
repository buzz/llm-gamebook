from collections.abc import Iterable

from openai.types.chat import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition

from llm_gamebook.story.base import BaseGraph, BaseNode, LlmFunctionMixin


class Location(BaseNode):
    def __init__(self, node_id: str, description: Iterable[str]) -> None:
        super().__init__(node_id)
        self.description = description


class LocationGraph(BaseGraph, LlmFunctionMixin):
    @staticmethod
    def _create_node(node_id: str, description: Iterable[str]) -> Location:
        return Location(node_id, description)

    @property
    def function_params(self) -> Iterable[ChatCompletionToolParam]:
        yield ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name="change_location",
                description="Player moves to another location.",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "enum": [edge.id for edge in self.current.edges],
                            "description": "The location to move to.",
                        },
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
                strict=True,
            ),
        )
