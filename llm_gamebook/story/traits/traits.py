from typing import Any

from llm_gamebook.story.entity import BaseStoryEntity
from llm_gamebook.story.traits.registry import trait

# @trait("conditioned")
# class ConditionedTrait(BaseStoryEntity):
#     def __init__(self, conditions: list[str] | None = None, *args: Any, **kwargs: Any):
#         super().__init__(*args, **kwargs)
#         self.conditions = conditions or []

#     def is_enabled(self) -> bool:
#         return all(cond.is_met() for cond in self.conditions)


@trait("described")
class DescribedTrait(BaseStoryEntity):
    """Adds LLM-facing fields to an entity."""

    def __init__(self, name: str, description: str | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.name = name
        self.description = description
