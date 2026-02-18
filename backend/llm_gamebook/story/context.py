from functools import cached_property
from typing import TYPE_CHECKING

import jinja2

from llm_gamebook.story.errors import EntityNotFoundError
from llm_gamebook.story.project import Project

from .session_state import FieldValue, SessionState, SessionStateData
from .store import Store

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
            return entity.model_dump().get(field_name)
        except EntityNotFoundError:
            return None

    def get_tools(self) -> "Iterable[StoryTool]":
        for entity_type in self._project.entity_type_map.values():
            yield from entity_type.get_tools()

    async def get_system_prompt(self) -> str:
        """Render system prompt."""
        ctx = self.get_template_context()
        return await self._jinja_env.get_template("system_prompt.md.jinja2").render_async(ctx)

    async def get_intro_message(self) -> str:
        """Render first message (request for story introduction)."""
        ctx = self.get_template_context()
        return await self._jinja_env.get_template("intro_message.md.jinja2").render_async(ctx)

    def get_template_context(self) -> dict[str, object]:
        # TODO: implement proper session-aware template context
        return {}

    @cached_property
    def _jinja_env(self) -> jinja2.Environment:
        return jinja2.Environment(
            loader=jinja2.PackageLoader(__name__, "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )
