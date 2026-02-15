## 1. Database Schema

- [ ] 1.1 Add `state: SessionStateData | None` field to `Message` model in `backend/llm_gamebook/db/models/message.py`
- [ ] 1.2 Add JSON column migration for SQLite (use SQLModel defaults for aiosqlite compatibility)
- [ ] 1.3 Update `to_dict()` method to include state field in serialization

## 2. SessionState Schema & Class

- [ ] 2.1 Create `backend/llm_gamebook/story/session_state.py` with Pydantic models:
  - `EntityRefSingle = {"type": "entity", "target": str}`
  - `EntityRefList = {"type": "entity-list", "target": list[str]}`
  - `FieldValue = str | bool | int | float | EntityRefSingle | EntityRefList`
  - `SessionStateData` model with `entities: dict[str, dict[str, FieldValue]]`
- [ ] 2.2 Create `SessionState` class wrapping `SessionStateData`
- [ ] 2.3 Implement `__init__` accepting optional `SessionStateData`
- [ ] 2.4 Implement `set_field(entity_id: str, field_name: str, value: FieldValue) -> None`
- [ ] 2.5 Implement `get_field(entity_id: str, field_name: str) -> FieldValue | None`
- [ ] 2.6 Implement `to_json() -> str` serialization method
- [ ] 2.7 Implement `from_json(json_str: str) -> SessionState` class method (validates via `SessionStateData`)
- [ ] 2.8 Implement `to_dict() -> dict` for internal use

## 3. StoryState Integration

- [ ] 3.1 Update `StoryState.__init__` to accept optional `session_state` parameter
- [ ] 3.2 Add `session_state` attribute to `StoryState`
- [ ] 3.3 Add `get_effective_field(entity_id: str, field_name: str) -> FieldValue | None` method
- [ ] 3.4 Add `set_field(entity_id: str, field_name: str, value: FieldValue) -> None` method
- [ ] 3.5 Implement merge logic: session override takes precedence over project default

## 4. State Persistence

- [ ] 4.1 Update message creation to pass state when saving responses
- [ ] 4.2 Implement `get_latest_state(session_id)` to find most recent message with state
- [ ] 4.3 Update session loading to restore state from latest response
- [ ] 4.4 Handle case where no state exists (new session)

## 5. Testing

- [ ] 5.1 Add unit tests for `SessionState` class (set/get/serialize/deserialize)
- [ ] 5.2 Add tests for effective field values (override vs default)
- [ ] 5.3 Add tests for orphaned field handling (project field removed)
- [ ] 5.4 Add tests for missing field handling (project adds new field)
- [ ] 5.5 Add integration test for state persistence through message flow

## 6. Error Handling

- [ ] 6.1 Validate entity_id exists in project when setting field
- [ ] 6.2 Validate state via `SessionStateData` Pydantic model on deserialization
- [ ] 6.3 Handle Pydantic validation errors gracefully with descriptive error message
