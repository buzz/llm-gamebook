## Context

The `StreamRunner.run()` method in `backend/llm_gamebook/engine/_runner.py` currently returns a 4-tuple that is difficult to read and maintain:

```python
async def run(
    self, msg_history: Sequence[ModelMessage], state: StoryState
) -> tuple[Sequence[ModelMessage], list[UUID], list[list[UUID]], dict[UUID, int]]:
```

This tuple contains:
1. `Sequence[ModelMessage]` - the message history after the run
2. `list[UUID]` - message IDs for the responses
3. `list[list[UUID]]` - part IDs for each message's parts
4. `dict[UUID, int]` - thinking durations keyed by part UUID

The caller in `StoryEngine.generate_response()` must unpack these in the correct order, making the code fragile and hard to read.

## Goals / Non-Goals

**Goals:**
- Add a typed return value (`StreamResult`) to replace the 4-tuple
- Provide semantic meaning to each returned field via docstrings
- Improve code readability and maintainability
- No behavioral changes - pure refactoring

**Non-Goals:**
- Modify the data being returned (same values, same logic)
- Add any new capabilities
- Change the WebSocket or API contracts

## Decisions

### Decision: Use dataclass over NamedTuple

**Chosen:** `dataclass` with `frozen=True` (immutable)

**Rationale:**
- Dataclasses support mutable default values during construction if needed
- Better IDE autocomplete - field names are explicit attributes
- Can add methods later if needed (e.g., helper functions)
- More familiar to most Python developers than NamedTuple

**Alternatives considered:**
- NamedTuple: Slightly more memory efficient, but less flexible
- Pydantic BaseModel: Overkill for internal use, adds dependency

### Decision: Include docstrings on each field

**Rationale:**
- The whole point is clarity - docstrings explain *what* each field is and *why* it exists
- Helps future developers understand the data flow without reading the implementation

## Risks / Trade-offs

- **Risk**: Minor - developers habit to tuple unpacking may need adjustment
  - **Mitigation**: The unpacking pattern `messages, message_ids, part_ids, durations = result` still works

- **Risk**: Adding a new type that could become stale if the return values change
  - **Mitigation**: The type will serve as documentation of the contract

## Migration Plan

This is an internal refactoring with no migration needed:
1. Add the `StreamResult` dataclass
2. Update return type annotation
3. Update caller to use `.field` access instead of tuple unpacking
4. Tests should pass without changes (same data returned)

## Open Questions

None - this is a straightforward refactoring with clear scope.
