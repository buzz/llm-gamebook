## Why

The current codebase loads project definitions (YAML) into entity objects but lacks a separate session state layer to track dynamic changes during gameplay. This prevents multiple save games, undo/redo, and condition-based triggers. Separating static project definitions from dynamic session state is foundational for enabling save/load, history traversal, and the trigger system.

## What Changes

- Add `state: dict | None` field to the `Message` model to persist session state with model responses
- Create `SessionState` class that holds entity field overrides as a dict structure
- Provide `get`/`set` methods on `SessionState` for entity fields with merging logic for project defaults
- Implement JSON serialization/deserialization for session state persistence
- Update `StoryState` to hold both project and session state
- Add method to compute effective field values combining session overrides + project defaults

## Capabilities

### New Capabilities

- `session-state`: Core infrastructure for persisting entity field overrides separately from project definition, enabling save/load and future trigger system

### Modified Capabilities

- (none)

## Impact

- **Database**: New `state` column on `Message` model
- **Backend**: New `SessionState` class, updates to `StoryState` integration
- **Testing**: New tests for state serialization, merge logic, and effective field evaluation
