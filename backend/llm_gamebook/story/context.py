from functools import cached_property
from typing import TYPE_CHECKING, cast

import jinja2

from llm_gamebook.story.errors import EntityNotFoundError
from llm_gamebook.story.project import Project

from .session_state import FieldValue, SessionState, SessionStateData
from .store import Store
from .template_view import TemplateContext

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .types import StoryTool


# TODO: prevent entity id collisions
class StoryContext:
    def __init__(
        self,
        project: Project,
        session_state: SessionStateData | None = None,
    ) -> None:
        super().__init__()
        self._project = project
        initial_state = SessionState(session_state)
        self._store = Store(initial_state=initial_state, load_trait_reducers=True)

    @property
    def project(self) -> "Project":
        return self._project

    @property
    def session_state(self) -> SessionState:
        return self._store.get_state()

    @property
    def store(self) -> Store:
        return self._store

    def get_effective_field(self, entity_id: str, field_name: str) -> FieldValue | None:
        session_value = self._store.get_state().get_field(entity_id, field_name)
        if session_value is not None:
            return session_value

        try:
            entity = self._project.get_entity(entity_id)
            return cast("FieldValue", getattr(entity, field_name))
        except (AttributeError, EntityNotFoundError):
            return None

    def get_tools(self) -> "Iterable[StoryTool]":
        for entity_type in self._project.entity_type_map.values():
            yield from entity_type.get_tools()

    async def get_system_prompt(self) -> str:
        """Render system prompt."""
        return await self._render_template("system_prompt")

    async def get_intro_message(self) -> str:
        """Render first message (request for story introduction)."""
        return await self._render_template("intro_message")

    async def _render_template(self, template_name: str) -> str:
        ctx = TemplateContext(self)
        template = self._jinja_env.get_template(f"{template_name}.md.jinja2")
        return await template.render_async(ctx)

    @cached_property
    def _jinja_env(self) -> jinja2.Environment:
        return jinja2.Environment(
            loader=jinja2.PackageLoader(__name__, "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )
