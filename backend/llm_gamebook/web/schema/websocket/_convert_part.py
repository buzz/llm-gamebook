import json
from functools import singledispatch
from uuid import UUID

import pydantic_ai

from llm_gamebook.web.schema.session.part import (
    ModelResponsePart,
    TextPart,
    ThinkingPart,
    ToolCallPart,
)


@singledispatch
def convert_part(part: object, part_id: UUID) -> ModelResponsePart:
    msg = f"Unknown part type: {type(part)}"
    raise TypeError(msg)


@convert_part.register
def _(part: pydantic_ai.TextPart, part_id: UUID) -> ModelResponsePart:
    return TextPart(id=part_id, content=part.content)


@convert_part.register
def _(part: pydantic_ai.ToolCallPart, part_id: UUID) -> ModelResponsePart:
    args = json.dumps(part.args) if isinstance(part.args, dict) else part.args
    return ToolCallPart(
        id=part_id,
        args=args,
        tool_name=part.tool_name,
        tool_call_id=part.tool_call_id,
    )


@convert_part.register
def _(part: pydantic_ai.ThinkingPart, part_id: UUID) -> ModelResponsePart:
    return ThinkingPart(
        id=part_id,
        content=part.content,
        provider_name=part.provider_name,
    )
