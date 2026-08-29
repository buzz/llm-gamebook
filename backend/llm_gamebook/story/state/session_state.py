from typing import TypedDict

from pydantic import BaseModel

from llm_gamebook.story.errors import DynamicFieldReadOnlyError, EntityFieldNotFoundError


class EntityRef(TypedDict):
    """A reference to a single entity."""

    type: str
    target: str


class EntityRefList(TypedDict):
    """A list of references to entities."""

    type: str
    target: list[str]


type FieldValue = str | bool | int | float | EntityRef | EntityRefList


class SessionStateData(BaseModel):
    entities: dict[str, dict[str, FieldValue]]


class SessionState:
    def __init__(
        self,
        data: SessionStateData | None = None,
        *,
        read_only_fields: frozenset[tuple[str, str]] | None = None,
    ) -> None:
        self._data = data or SessionStateData(entities={})
        self._read_only_fields = read_only_fields if read_only_fields is not None else frozenset()

    @property
    def read_only_fields(self) -> frozenset[tuple[str, str]]:
        """(entity_id, field_name) pairs derived from dynamic expressions.

        Session state may never override these fields: their effective value
        is always recomputed from the project's dynamic field definitions.
        """
        return self._read_only_fields

    def _assert_writable(self, entity_id: str, field_name: str) -> None:
        """Raise if the field is read-only (derived from a dynamic expression)."""
        if (entity_id, field_name) in self._read_only_fields:
            msg = (
                f"Field '{entity_id}.{field_name}' is read-only: it is derived from a "
                "dynamic expression and cannot be overridden in session state"
            )
            raise DynamicFieldReadOnlyError(msg)

    def set_field(self, entity_id: str, field_name: str, value: FieldValue) -> None:
        self._assert_writable(entity_id, field_name)
        if entity_id not in self._data.entities:
            self._data.entities[entity_id] = {}
        self._data.entities[entity_id][field_name] = value

    def get_field(self, entity_id: str, field_name: str) -> FieldValue:
        try:
            entity = self._data.entities[entity_id]
            return entity[field_name]
        except KeyError as e:
            msg = f"Field state '{field_name}' not found on entity '{entity_id}'"
            raise EntityFieldNotFoundError(msg) from e

    def is_empty(self) -> bool:
        return not self._data.entities

    @property
    def data(self) -> SessionStateData:
        return self._data

    def to_json(self) -> str:
        return self._data.model_dump_json()

    @classmethod
    def from_json(
        cls,
        json_str: str,
        *,
        read_only_fields: frozenset[tuple[str, str]] | None = None,
    ) -> "SessionState":
        data = SessionStateData.model_validate_json(json_str)
        return cls(data, read_only_fields=read_only_fields)
