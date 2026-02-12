from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from llm_gamebook.story.trait_registry import trait_registry
from llm_gamebook.story.types import NormalizedPascalCase, NormalizedSnakeCase
from llm_gamebook.utils import normalized_pascal_case, normalized_snake_case

from .validators import id_from_name


class TraitDefinition(BaseModel):
    name: NormalizedSnakeCase
    """The name for the trait."""

    options: dict[str, object] = Field(default_factory=dict)
    """The trait's options."""

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, data: object) -> dict[str, object]:
        """
        Normalizes trait definitions.
        Supports:
          1. Shorthand: "trait_name"
          2. Inline: {"name": "trait_name", "param": "val"}
          3. Explicit: {"name": "trait_name", "options": {"param": "val"}}
        """
        if isinstance(data, str):
            return {"name": data, "options": {}}

        if not isinstance(data, dict):
            msg = f"Expected str or dict for trait, got {type(data).__name__}"
            raise TypeError(msg)

        # Work on a copy to avoid mutating input
        payload = dict(data)

        # Extract 'name'
        name = payload.pop("name", None)
        if not name:
            msg = "Trait definition dictionary must contain a 'name' key"
            raise ValueError(msg)

        # Extract existing 'options' if they exist (prevents 'options': {'options': ...} nesting)
        options = payload.pop("options", {})
        options = (
            # Copy to avoid mutating original nested dict
            dict(options)
            if isinstance(options, dict)
            # Handle cases where 'options' might be a single value (e.g., a string or int)
            else {"value": options}
        )

        # Lift remaining fields into options
        # Anything left in payload (after popping 'name' and 'options') is merged into the dict
        options.update(payload)

        return {
            "name": name,
            "options": options,
        }

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

    functions: list[FunctionDefinition] | None = None
    """List of tool functions the LLM may call."""

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

    @model_validator(mode="before")
    @classmethod
    def id_from_name(cls, data: object) -> object:
        return id_from_name(data, normalized_pascal_case)
