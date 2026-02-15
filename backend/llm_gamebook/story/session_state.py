from typing import TypedDict

from pydantic import BaseModel


class EntityRefSingle(TypedDict):
    type: str
    target: str


class EntityRefList(TypedDict):
    type: str
    target: list[str]


type FieldValue = str | bool | int | float | EntityRefSingle | EntityRefList


class SessionStateData(BaseModel):
    entities: dict[str, dict[str, FieldValue]]


class SessionState:
    def __init__(self, data: SessionStateData | None = None) -> None:
        self._data = data or SessionStateData(entities={})

    def set_field(self, entity_id: str, field_name: str, value: FieldValue) -> None:
        if entity_id not in self._data.entities:
            self._data.entities[entity_id] = {}
        self._data.entities[entity_id][field_name] = value

    def get_field(self, entity_id: str, field_name: str) -> FieldValue | None:
        return self._data.entities.get(entity_id, {}).get(field_name)

    def to_json(self) -> str:
        return self._data.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "SessionState":
        data = SessionStateData.model_validate_json(json_str)
        return cls(data)
