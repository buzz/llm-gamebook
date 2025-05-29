from typing import Any

from pydantic import BaseModel, field_validator, model_validator

from llm_gamebook.schema.base import BaseEntity, Slug
from llm_gamebook.schema.validators import derive_from_name
from llm_gamebook.story.traits.registry import trait_registry


class TraitSpec(BaseModel):
    name: Slug
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


class EntityDefinition(BaseModel):
    """A definition of a story entity type."""

    slug: Slug
    name: str
    instructions: str | None = None
    traits: list[TraitSpec] = []
    instances: list[BaseEntity]

    @model_validator(mode="before")
    @classmethod
    def derive_slug_from_name(cls, data: Any) -> Any:
        return derive_from_name(data)
