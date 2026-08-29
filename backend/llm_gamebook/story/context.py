from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING, cast
from uuid import UUID

import jinja2

from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.conditions.evaluator import BoolExprEvaluator
from llm_gamebook.story.errors import (
    DynamicFieldEvalError,
    EntityFieldNotFoundError,
    EntityNotFoundError,
    ExpressionEvalError,
)
from llm_gamebook.story.schemas import Project
from llm_gamebook.story.schemas.expression import ValueExprDefinition
from llm_gamebook.story.schemas.project import collect_dynamic_fields

from .state import (
    FieldValue,
    SessionState,
    SessionStateData,
    Store,
    auto_save_middleware,
    logging_middleware,
    message_bus_publisher_middleware,
    trigger_eval_middleware,
)
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
        session_id: UUID | None = None,
        message_bus: MessageBus | None = None,
    ) -> None:
        super().__init__()
        self._project = project
        self._dynamic_fields: dict[tuple[str, str], ValueExprDefinition] = collect_dynamic_fields(
            project
        )
        self._read_only_fields = frozenset(self._dynamic_fields)
        initial_state = SessionState(session_state, read_only_fields=self._read_only_fields)
        self._store = Store(
            initial_state,
            middleware=[
                logging_middleware,
                message_bus_publisher_middleware(message_bus, session_id),
                trigger_eval_middleware(self),
                auto_save_middleware,
            ],
        )

    @property
    def project(self) -> "Project":
        return self._project

    @property
    def read_only_fields(self) -> frozenset[tuple[str, str]]:
        """Field coordinates session state may not override (dynamic fields)."""
        return self._read_only_fields

    @property
    def evaluator(self) -> BoolExprEvaluator:
        """The expression evaluator bound to this project and context."""
        return self._evaluator

    @cached_property
    def _evaluator(self) -> BoolExprEvaluator:
        return BoolExprEvaluator(self._project, self)

    @property
    def session_state(self) -> SessionState:
        return self._store.get_state()

    @property
    def store(self) -> Store:
        return self._store

    def get_field(self, entity_id: str, field_name: str) -> FieldValue:
        """Retrieve an effective entity field value.

        Resolution order: session override, then dynamic field expression
        (evaluated against current effective state), then the project
        default.

        Raises:
            DynamicFieldEvalError: If a dynamic field's expression fails.
            EntityFieldNotFoundError: If no tier resolves the field.
        """
        # 1) Session override
        with suppress(EntityFieldNotFoundError):
            return self._store.get_state().get_field(entity_id, field_name)

        # 2) Dynamic field definition
        definition = self._dynamic_fields.get((entity_id, field_name))
        if definition is not None:
            return self._eval_dynamic_field(entity_id, field_name, definition)

        # 3) Default from project definition
        with suppress(AttributeError, EntityNotFoundError):
            entity = self._project.get_entity(entity_id)
            value = getattr(entity, field_name)
            return cast("FieldValue", value)

        msg = f"Field '{field_name}' not found on entity '{entity_id}'"
        raise EntityFieldNotFoundError(msg)

    def _eval_dynamic_field(
        self,
        entity_id: str,
        field_name: str,
        definition: ValueExprDefinition,
    ) -> FieldValue:
        """Evaluate a dynamic field definition against the current effective state."""
        try:
            value = self._evaluator.eval_value(definition.value)
        except ExpressionEvalError as err:
            field = f"{entity_id}.{field_name}"
            raise DynamicFieldEvalError(str(err), field=field, source=definition.source) from err
        return cast("FieldValue", value)

    def validate_entity_exists(self, entity_id: str) -> bool:
        try:
            self._project.get_entity(entity_id)
        except EntityNotFoundError:
            return False
        else:
            return True

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
