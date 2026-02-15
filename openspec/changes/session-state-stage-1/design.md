## Context

The current codebase loads project definitions (YAML) into `Project` and `Entity` objects at startup. Each entity has static field values from the YAML. When the graph trait transitions between nodes, it mutates entity fields directly. There is no separation between the static project definition and dynamic runtime changes.

This design addresses Stage 1: adding database support for session state and creating the core `SessionState` class that holds entity field overrides separately from project defaults.

## Goals / Non-Goals

**Goals:**
- Add `state: dict | None` column to `Message` model for persisting session state
- Create `SessionState` class to hold entity field overrides as a dict structure
- Provide `get_field`/`set_field` methods for reading/writing entity fields with automatic merge of project defaults
- Implement JSON serialization/deserialization for state persistence
- Update `StoryState` to own a `SessionState` instance and expose effective field values

**Non-Goals:**
- Action system (Stage 2)
- Action-driven state changes (Stage 3)
- Trigger system (Stage 4)
- History/undo (Stage 5)
- Dynamic field evaluation (`=expression` syntax)

## Decisions

### 1. State Storage: JSON column on Message model

**Decision:** Store session state as a JSON column on the `Message` model.

**Rationale:** The architecture specifies that state is stored with model responses. The latest response with a non-null state is the current state. This enables history traversal for undo/fork later.

**Alternatives considered:**
- Separate `SessionState` table: Would require additional joins and sync logic
- Store in `Session` model: Doesn't support history traversal per response

### 2. SessionState Structure: Entity-level overrides dict

**Decision:** Store state as `{entity_id: {field_name: value}}` where only overridden fields are recorded.

**Rationale:**
- Sparse storage: Only changed fields are stored, defaults come from project
- Simple merge logic: Override dict merged with project defaults at read time
- Future-proof: Easy to extend with additional metadata per entity

**Alternatives considered:**
- Full state snapshot: Would duplicate all project fields, harder to diff
- Field-level separate table: More complex queries, over-engineered for Stage 1

### 3. Merge Strategy: Read-time resolution

**Decision:** Compute effective field value at read time by merging session overrides with project defaults.

**Rationale:**
- Project can change between sessions (new default values)
- Always uses latest project defaults as base
- Simpler than versioning state with project schema

**Alternatives considered:**
- Store full effective state: Loses ability to re-apply new defaults
- Snapshot project with state: Couples state to specific project version

### 4. StoryState Integration: Composition over inheritance

**Decision:** `StoryState` holds a `SessionState` instance as an attribute, not inheritance.

**Rationale:**
- Clear separation of concerns
- Easier to test independently
- Follows composition principle in existing code

### 5. Session State Schema: Dynamic Pydantic Model

**Decision:** Define a Pydantic model `SessionStateData` that validates the JSON blob structure while accepting arbitrary keys.

**Schema:**
```python
type FieldValue = str | bool | int | float | EntityRefValue
type EntityRefValue = EntityRefSingle | EntityRefList
type EntityRefSingle = {"type": "entity", "target": str}
type EntityRefList = {"type": "entity-list", "target": list[str]}

class SessionStateData(BaseModel):
    entities: dict[str, dict[str, FieldValue]]
```

**Rationale:**
- Validates JSON structure on deserialization
- Accepts arbitrary entity IDs and field names (dynamic project)
- Differentiates entity references from plain strings via `{"type": "entity", ...}` wrapper
- Future-proof: can extend with additional types later

**Alternatives considered:**
- Raw dict without validation: Loses type safety, harder to debug corruption
- Static schema per project: Would require generating schema at project load time, more complex

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Entity field changes not persisted | Ensure all state modifications go through `SessionState.set_field()` |
| State corruption on invalid data | Validate state dict structure on deserialization |
| Orphaned fields when project changes | Handle gracefully in merge: drop fields not in project |
| Missing fields when project adds new | Use project defaults for missing fields in merge |
| Large state blob affecting performance | Monitor size; consider compression if needed |

## Migration Plan

1. **Database migration**: Add nullable `state` JSON column to `Message` table
2. **New `SessionState` class**: Create `backend/llm_gamebook/story/session_state.py`
3. **Update `StoryState`**: Add `session_state` attribute and effective field methods
4. **Update message creation**: Pass state when saving responses
5. **Update session loading**: Load latest state from most recent response with state
6. **Tests**: Add tests for state serialization, merge logic, effective values

## Open Questions

- Should state be stored on response messages only, or also requests?
  - Current design: only responses (following architecture)
- How to handle concurrent sessions with same project?
  - Each session has own messages, state stored per message
- Should we index the state column?
  - Not needed for Stage 1; add if queries become slow
