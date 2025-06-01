from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from llm_gamebook.schema.validators import pascal_case_from_name, snake_case_from_name
from llm_gamebook.story.traits.registry import trait_registry
from llm_gamebook.types import NormalizedPascalCase, NormalizedSnakeCase


class TraitSpec(BaseModel):
    name: NormalizedSnakeCase
    params: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, data: Any) -> dict[str, Any]:
        """Transform both variants (`str`, `dict`) into `dict` with `params` field."""
        if isinstance(data, str):
            return {"name": data}
        if isinstance(data, dict):
            # Lift additional fields into params
            known = {"name"}
            return {
                "name": data["name"],
                "params": {k: v for k, v in data.items() if k not in known},
            }
        return data

    @field_validator("name")
    @classmethod
    def is_valid_trait_name(cls, value: str) -> str:
        if value not in trait_registry:
            msg = f"Unknown entity trait: '{value}'"
            raise ValueError(msg)
        return value


class FunctionSpec(BaseModel):
    """A definition of an LLM-called function for the entity."""

    target: str
    """The target method to call on the entity."""

    name: str | None = None
    """The name for the function."""

    description: str | None = None
    """The description for the function."""

    properties: dict[str, str] | None = None
    """Maps function argument properties to description."""


class BaseEntity(BaseModel):
    """The base class to all story entities."""

    # Preserve extra attributes for mixins/traits
    model_config = ConfigDict(extra="allow")

    id: NormalizedSnakeCase
    """A unique identifier."""

    @model_validator(mode="before")
    @classmethod
    def snake_case_from_name(cls, data: Any) -> Any:
        return snake_case_from_name(data)


class EntityDefinition(BaseModel):
    """A definition of a story entity type."""

    id: NormalizedPascalCase
    name: str
    instructions: str | None = None
    traits: list[TraitSpec] = []
    entities: list[BaseEntity]
    functions: list[FunctionSpec] | None = None

    @model_validator(mode="before")
    @classmethod
    def pascal_case_from_name(cls, data: Any) -> Any:
        return pascal_case_from_name(data)
