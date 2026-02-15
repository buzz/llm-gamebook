## Why

The `StreamRunner.run()` method currently returns a wild 4-tuple:
```python
tuple[Sequence[ModelMessage], list[UUID], list[list[UUID]], dict[UUID, int]]
```

This is unreadable, error-prone (easy to mix up argument order), and provides no semantic meaning to the returned values. Adding a proper return type improves code clarity and maintainability without changing any behavior.

## What Changes

- Add a new `StreamResult` class (NamedTuple or dataclass) in `backend/llm_gamebook/engine/_runner.py`
- The class will have four fields with descriptive names and docstrings:
  - `messages`: The resulting ModelMessage sequence
  - `message_ids`: UUIDs for each message
  - `part_ids`: Nested UUIDs for each part within each message
  - `durations`: Thinking durations mapped by part UUID
- Update `StreamRunner.run()` return type annotation to use `StreamResult`
- Update `StoryEngine.generate_response()` to use the new return type

## Capabilities

### New Capabilities
None - this is a refactoring change with no new behavior.

### Modified Capabilities
None - existing behavior is preserved.

## Impact

- **Affected code**:
  - `backend/llm_gamebook/engine/_runner.py` - add StreamResult class, update return type
  - `backend/llm_gamebook/engine/engine.py` - update caller to use typed return value
- **No breaking changes** - the data returned is identical, only the type wrapper changes
- **No API changes** - internal refactoring only
