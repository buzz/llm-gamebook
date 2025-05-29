from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

from llm_gamebook.schema.validators import derive_from_name, is_slug

Slug = Annotated[str, AfterValidator(is_slug)]


class BaseEntity(BaseModel):
    """The base class to all story entities."""

    # Preserve extra attributes for mixins/traits
    model_config = ConfigDict(extra="allow")

    slug: Slug
    """A unique identifier."""

    @model_validator(mode="before")
    @classmethod
    def derive_slug_from_name(cls, data: Any) -> Any:
        return derive_from_name(data)
