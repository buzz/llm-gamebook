from functools import cached_property
from typing import TYPE_CHECKING, Self

import jinja2
from pydantic_ai import RunContext

from llm_gamebook.story.project import Project

if TYPE_CHECKING:
    from collections.abc import Iterable

    from llm_gamebook.types import StoryTool


# TODO: prevent entity id collisions
class StoryState:
    def __init__(
        self,
        project: Project,
    ) -> None:
        super().__init__()
        self._project = project

    @property
    def project(self) -> "Project":
        return self._project

    def get_tools(self) -> "Iterable[StoryTool]":
        for entity_type in self._project.entity_type_map.values():
            yield from entity_type.get_tools()

    async def get_system_prompt(self) -> str:
        """Render system prompt."""
        ctx = self._project.get_template_context()
        return await self._jinja_env.get_template("system_prompt.md.jinja2").render_async(ctx)

    async def get_intro_message(self) -> str:
        """Render first message (request for story introduction)."""
        ctx = self._project.get_template_context()
        return await self._jinja_env.get_template("intro_message.md.jinja2").render_async(ctx)

    @cached_property
    def _jinja_env(self) -> jinja2.Environment:
        return jinja2.Environment(
            loader=jinja2.PackageLoader(__name__, "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )
