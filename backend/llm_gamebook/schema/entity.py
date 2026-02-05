from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from llm_gamebook.schema.validators import id_from_name
from llm_gamebook.story.trait_registry import trait_registry
from llm_gamebook.types import NormalizedPascalCase, NormalizedSnakeCase
from llm_gamebook.utils import normalized_pascal_case, normalized_snake_case


class TraitDefinition(BaseModel):
    name: NormalizedSnakeCase
    """The name for the trait."""

    options: dict[str, object] | None = None
    """The trait's options."""

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, data: object) -> dict[str, object]:
        """Transform both variants (`str`, `dict`) into `dict` with `options` field."""
        if isinstance(data, str):
            return {"name": data}
        if isinstance(data, dict):
            # Lift additional fields into options
            known = {"name"}
            name = data["name"]
            if isinstance(name, str):
                return {
                    "name": data["name"],
                    "options": {k: v for k, v in data.items() if k not in known},
                }
            msg = "Expecting name to be str"
            raise ValueError(msg)
        msg = "Expecting data to be str or dict"
        raise ValueError(msg)

    @field_validator("name")
    @classmethod
    def is_valid_trait_name(cls, value: str) -> str:
        if value not in trait_registry:
            msg = f"Unknown entity trait: '{value}'"
            raise ValueError(msg)
        return value


class FunctionDefinition(BaseModel):
    """A definition of an LLM-called function for the entity."""

    target: str
    """The target method to call on the entity."""

    name: str | None = None
    """The name for the function."""

    description: str | None = None
    """The description for the function."""

    properties: dict[str, str] | None = None
    """Maps function argument properties to description."""


class EntityDefinition(BaseModel):
    """The base class to all story entities."""

    # Preserve extra attributes for mixins/traits
    model_config = ConfigDict(extra="allow")

    id: NormalizedSnakeCase
    """A unique identifier (snake_case)."""

    @model_validator(mode="before")
    @classmethod
    def id_from_name(cls, data: object) -> object:
        return id_from_name(data, normalized_snake_case)


class EntityTypeDefinition(BaseModel):
    """A definition of a story entity type."""

    id: NormalizedPascalCase
    """A unique identifier (PascalCase)."""

    name: str
    """Human-readable name of the entity type presented to the LLM."""

    instructions: str | None = None
    """Instructions text for this entity type presented to the LLM."""

    traits: list[TraitDefinition] = []
    """List of traits for entities of this type."""

    entities: list[EntityDefinition]
    """List of entity definitions."""

    functions: list[FunctionDefinition] | None = None
    """List of tool functions the LLM may call."""

    @model_validator(mode="before")
    @classmethod
    def id_from_name(cls, data: object) -> object:
        return id_from_name(data, normalized_pascal_case)
