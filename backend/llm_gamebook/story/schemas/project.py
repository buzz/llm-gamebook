from collections.abc import Iterator, Mapping
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Self, overload

import yaml
from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, ValidationError, model_validator

from llm_gamebook.constants import PROJECT_FILENAME
from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.conditions.grammar import parse_bool_expr
from llm_gamebook.story.errors import (
    EntityNotFoundError,
    EntityTypeNotFoundError,
    ProjectExistsError,
)
from llm_gamebook.story.schemas.entity import BaseEntity, EntityType, EntityTypeDefinition
from llm_gamebook.story.schemas.expression import ValueExprDefinition

from .validators import is_valid_project_id


class ProjectSource(StrEnum):
    EXAMPLE = auto()
    LOCAL = auto()


type ProjectId = Annotated[str, AfterValidator(is_valid_project_id)]


class ProjectDefinition(BaseModel):
    """Gamebook project definition loaded from external file."""

    id: ProjectId = Field(exclude=True)
    """The project ID in the format `namespace/name`."""

    source: ProjectSource = Field(exclude=True)
    """The project source type."""

    title: str
    """The project title."""

    author: str | None = None
    """The project author."""

    description: str | None
    """The project description."""

    image: str | None = Field(exclude=True, default=None)
    """The project image."""

    entity_types: list[EntityTypeDefinition] = Field(default_factory=list)
    """Definition of entity types."""

    def __str__(self) -> str:
        return f'<{type(self).__name__} id="{self.id}" title="{self.title}" source="{self.source}">'

    @property
    def namespace(self) -> str:
        return self.id.split("/", 1)[0]

    @property
    def name(self) -> str:
        return self.id.split("/", 1)[1]

    def save(self, save_path: Path) -> None:
        try:
            save_path.mkdir(parents=True)
        except FileExistsError as e:
            msg = f"Project '{self.id}' already exists"
            raise ProjectExistsError(msg) from e

        yaml_path = save_path / PROJECT_FILENAME
        yaml_path.write_text(yaml.dump(self.model_dump()))

    @model_validator(mode="after")
    def validate_trigger_conditions(self) -> Self:
        """Validate that all trigger conditions are parseable boolean expressions."""
        for entity_type in self.entity_types:
            for trigger in entity_type.triggers:
                try:
                    parse_bool_expr(trigger.condition)
                except ValueError as err:
                    msg = (
                        f"Invalid trigger condition for entity type '{entity_type.id}' "
                        f"and trigger '{trigger.name}': {err}"
                    )
                    raise ValueError(msg) from err
        return self

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        namespace = project_path.parts[-2]
        name = project_path.parts[-1]
        project_filepath = project_path / PROJECT_FILENAME

        try:
            data = yaml.safe_load(project_filepath.read_text())
        except FileNotFoundError as err:
            msg = f"Project file not found: {project_filepath}"
            raise FileNotFoundError(msg) from err

        return cls.model_validate(
            {
                **data,
                "id": f"{namespace}/{name}",
                "source": ProjectSource.LOCAL,
            },
            strict=True,
        )


def iter_entity_field_values(entity: BaseEntity) -> list[tuple[str, object]]:
    """Collect (field_name, value) pairs for an entity's field values.

    Covers both pydantic fields declared by trait base classes and arbitrary
    YAML attributes captured via extra="allow".

    Args:
        entity: The runtime entity to inspect.

    Returns:
        The field name and value pairs, in declaration then YAML order.
    """
    values = [(name, getattr(entity, name)) for name in type(entity).model_fields]
    extra = entity.__pydantic_extra__
    if extra:
        values.extend(extra.items())
    return values


def convert_dynamic_fields(project: "Project") -> None:
    """Replace `=`-prefixed string field values with parsed ValueExprDefinition.

    Scans declared model fields and extra attributes of every entity
    (design D3). A parse failure raises ValueError naming the entity, field,
    and the parse problem, failing project load.

    Args:
        project: The runtime project whose entities to convert.
    """
    for entity_type in project.entity_type_map.values():
        for entity in entity_type.entity_map.values():
            for name, value in iter_entity_field_values(entity):
                if not (isinstance(value, str) and value.startswith("=")):
                    continue
                try:
                    converted = ValueExprDefinition.model_validate(value)
                except ValidationError as err:
                    msg = (
                        f"Entity '{entity.id}' field '{name}': "
                        f"invalid dynamic field expression: {err}"
                    )
                    raise ValueError(msg) from err
                try:
                    setattr(entity, name, converted)
                except AttributeError as err:
                    msg = (
                        f"Entity '{entity.id}' field '{name}' cannot be a dynamic field: "
                        f"it is a read-only property"
                    )
                    raise ValueError(msg) from err


def collect_dynamic_fields(project: "Project") -> dict[tuple[str, str], ValueExprDefinition]:
    """Map (entity_id, field_name) -> definition for all dynamic fields in a project.

    Args:
        project: The runtime project to scan (dynamic fields must be converted).

    Returns:
        The dynamic field definitions keyed by (entity_id, field_name).
    """
    fields: dict[tuple[str, str], ValueExprDefinition] = {}
    for entity_type in project.entity_type_map.values():
        for entity in entity_type.entity_map.values():
            for name, value in iter_entity_field_values(entity):
                if isinstance(value, ValueExprDefinition):
                    fields[entity.id, name] = value
    return fields


def _dynamic_field_head_refs(expr: g.Expr) -> Iterator[tuple[str, str]]:
    """Yield (entity_id, first_property) for every dot path in an expression.

    Only the head of a dot path can reference a dynamic field: deeper
    properties resolve to values (or fail), so they cannot continue a
    dependency chain (design D7).
    """
    if isinstance(expr, g.DotPath) and expr.property_chain:
        yield (expr.entity_id.value, expr.property_chain[0].value)
    if isinstance(expr, (g.ArithExpr, g.Comparison, g.AndExpr, g.OrExpr)):
        yield from _dynamic_field_head_refs(expr.left)
        yield from _dynamic_field_head_refs(expr.right)
    elif isinstance(expr, g.NotExpr):
        yield from _dynamic_field_head_refs(expr.expr)


def _find_dynamic_field_cycle(
    deps: dict[tuple[str, str], set[tuple[str, str]]],
) -> list[tuple[str, str]] | None:
    """Find a cycle in the dynamic field dependency graph via DFS.

    Args:
        deps: Mapping of dynamic field -> the dynamic fields it references.

    Returns:
        The cycle as a node path with the first node repeated at the end
        (e.g. [(a, x), (b, y), (a, x)]), or None if the graph is acyclic.
    """
    state: dict[tuple[str, str], int] = dict.fromkeys(deps, 0)
    stack: list[tuple[str, str]] = []

    def visit(node: tuple[str, str]) -> list[tuple[str, str]] | None:
        state[node] = 1
        stack.append(node)
        for neighbor in sorted(deps[node]):
            if state[neighbor] == 1:
                start = stack.index(neighbor)
                return [*stack[start:], neighbor]
            if state[neighbor] == 0:
                cycle = visit(neighbor)
                if cycle is not None:
                    return cycle
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(deps):
        if state[node] == 0:
            cycle = visit(node)
            if cycle is not None:
                return cycle
    return None


def detect_dynamic_field_cycles(project: "Project") -> None:
    """Fail project load on circular dynamic field dependencies (design D7).

    Builds the head-reference dependency graph over dynamic fields (edge
    A -> B when A's expression references dynamic field B) and raises
    ValueError naming the cycle path (e.g. `a.x -> b.y -> a.x`).

    Args:
        project: The runtime project to check (dynamic fields must be converted).
    """
    fields = collect_dynamic_fields(project)
    deps: dict[tuple[str, str], set[tuple[str, str]]] = {}
    for key in fields:
        deps[key] = set()
    for key, definition in fields.items():
        for ref in _dynamic_field_head_refs(definition.value):
            if ref in fields:
                deps[key].add(ref)

    cycle = _find_dynamic_field_cycle(deps)
    if cycle is not None:
        path = " \u2192 ".join(f"{entity_id}.{field_name}" for entity_id, field_name in cycle)
        msg = f"Circular dynamic field dependency: {path}"
        raise ValueError(msg)


class Project(ProjectDefinition):
    """Runtime representation of a gamebook project."""

    _entity_type_map: Mapping[str, EntityType] = PrivateAttr()

    @property
    def entity_type_map(self) -> Mapping[str, EntityType]:
        return self._entity_type_map

    def get_template_context(self) -> Mapping[str, object]:
        return {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "entity_types": [et.get_template_context() for et in self._entity_type_map.values()],
        }

    def get_entity_type(self, entity_type_id: str) -> EntityType:
        try:
            return self.entity_type_map[entity_type_id]
        except KeyError as err:
            msg = f"Entity type not found: {entity_type_id}"
            raise EntityTypeNotFoundError(msg) from err

    @overload
    def get_entity(self, entity_id: str) -> BaseEntity: ...
    @overload
    def get_entity[T: BaseEntity](self, entity_id: str, model: type[T]) -> T: ...
    def get_entity[T: BaseEntity](
        self, entity_id: str, model: type[T] | None = None
    ) -> BaseEntity | T:
        try:
            entity = next(
                e
                for entity_type in self.entity_type_map.values()
                for e in entity_type.entity_map.values()
                if e.id == entity_id
            )
        except StopIteration as err:
            msg = f"Entity not found: {entity_id}"
            raise EntityNotFoundError(msg) from err

        if not isinstance(entity, model or BaseEntity):
            msg = f"Entity has unexpected type: {type(entity).__name__}"
            raise TypeError(msg)

        return entity

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        project_def = super().from_path(project_path)
        return cls.from_definition(project_def)

    @classmethod
    def from_data(cls, data: object) -> Self:
        project_def = super().model_validate(data, strict=True)
        return cls.from_definition(project_def)

    @classmethod
    def from_definition(cls, project_def: ProjectDefinition) -> Self:
        """Initialize runtime project from definition."""
        project = cls.model_validate(project_def, from_attributes=True)

        entity_types = (EntityType.from_definition(et, project) for et in project_def.entity_types)
        project._entity_type_map = {et.id: et for et in entity_types}

        for entity_type in project.entity_type_map.values():
            entity_type.post_init()

        convert_dynamic_fields(project)
        detect_dynamic_field_cycles(project)

        return project
