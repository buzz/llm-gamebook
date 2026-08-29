# Session State Architecture

> **Status:** This is the **authoritative design** for session state in llm-gamebook.
> The current implementation state is described in [`docs/architecture.md`](../architecture.md);
> the stage-by-stage rollout plan (mapped to OpenSpec changes) is in [steps-overview.md](steps-overview.md).

## Overview

Separates the static project definition (from YAML) from dynamic session state, enabling:
- Multiple save games / snapshots
- Undo/redo
- Clean persistence
- Trigger system

## Core Concepts

### Project Definition (Static)

Loaded from YAML. Contains:
- Entity type definitions
- Entity default values (static fields)
- Trait configurations
- Trigger definitions (condition → action mappings)

### Session State (Dynamic)

Persisted separately. Contains:
- Entity field overrides (what changed from defaults)
- Stored with model responses
  - model responses have a `state` JSON blob field
  - enables going back in time (undo)
- Latest state is the latest model response that has its `state` field set (responses may omit storing state if there were no changes)

### Dynamic Fields (implemented)

Any entity field can be either:
- **Static**: literal value in YAML
- **Dynamic**: string prefixed with `=`, parsed at load time into a
  value-expression AST (`ValueExprDefinition`) and evaluated lazily on every read

```yaml
entities:
  - id: player
    max_hp: 10                       # static
    health: =player.max_hp - 5       # dynamic
```

**Expression language.** Dynamic fields share the condition grammar:
- References: `entity.property` dot paths (traversable into collections)
- Literals: numbers, strings, `true` / `false`
- Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`, `in` (single comparison, no chaining)
- Arithmetic: `+`, `-`, `*`, `/` (numeric operands only; `/` yields a float,
  int `/` int is exact float division; int `+`/`-`/`*` stay int)
- Boolean combinators: `not`, `and`, `or` (comparison results and plain
  references are usable as boolean values)

**Read-only semantics.** Dynamic fields are computed, not stored:
- They are never written into session state and never appear in state snapshots
- `SessionState.set_field` / `remove_field` on a dynamic field raises
  `DynamicFieldReadOnlyError`; `restore_defaults` ignores them
- Reads always re-evaluate against the current effective state

**Resolution order** (`StoryContext.get_field`):
1. Session-state override (of another, stored field)
2. Dynamic expression, evaluated against effective state
3. Entity default value

Session overrides of the fields a dynamic expression *reads* are picked up
(overrides shadow defaults as expression inputs); the dynamic field itself
cannot be overridden.

**Load-time guarantees.** When the project loads:
- Every `=...` string field is parsed; a syntax error fails the load
- Cyclic dependencies between dynamic fields (via dot-path head references)
  fail the load, e.g. `a.x → b.y → a.x`
- Fields managed by trait properties (e.g. `current_node_id` on graph
  entities) cannot be dynamic; this also fails the load

**Runtime errors.** A dynamic field whose expression fails at runtime (e.g.
missing reference, division by zero, non-numeric arithmetic operand) raises
`DynamicFieldEvalError` naming the `entity.field` and the source expression.
Trigger conditions, templates, and tools read dynamic fields transparently
through `StoryContext.get_field` and inherit this behavior.

See the broken-bulb example for a dynamic field read by a trigger:
`main.meeting_progress: =the_meeting.current_node_id == "leaflet_found"`.

## Action System

Actions are the only way to change state. Namespaced: `namespace/action`.

```yaml
triggers:
  - name: graph/transition
    condition: =player.has_visited('village')
    args:
      to: unlock_ending
```

### Built-in Actions

| Namespace | Actions |
|-----------|---------|
| `core` | `end-game`, `reset-game`, … |
| `graph` | `transition` |
| … | … |

### Tool → Action

LLM tools expose actions. Tool calls dispatch actions.

To expose a tool call to the LLM it needs to be mapped:
```
entities:
  - name: Main
    # ...
    functions:
      - action: graph/transition
        name: progress_main_story
        description: Progress the main story arc to the next node.
        properties:
          to: The next node in the main story arc.
        enabled: =player.has_visited('village')  # optional
```

## State Management (Redux-inspired)

```
Action → Middleware Chain → Reducer → New State
                    │
          ┌────────┼────────┼────────┐
          ▼        ▼        ▼        ▼
       Logger   Bridge    Triggers  AutoSave
```

### Middleware

Chain of functions `(Store, Action) → Action`:

1. **Logger** - logs all actions
2. **MessageBusPublisher** - publishes actions to the message bus
3. **TriggerEval** - evaluates all triggers, dispatches actions
4. **AutoSave** - persists session to disk

### Store

- Holds current state
- Dispatches actions through middleware
- Middleware can dispatch more actions
- Reducers are composed (chained)

### Reducers

Pure functions: `(State, Action) → State`

Traits can define reducers for actions:
```python
@staticmethod
def reducers():
    return {GraphTransitionAction: graph_transition_reducer}
```

### MessageBusPublisher

The **MessageBusPublisher** middleware bridges the action system to the application's message bus. After an action is dispatched but before state changes are applied, it optionally publishes an `ActionDispatched` message to the message bus.

**Purpose:**
- Enables the LLM to signal directly into the core application logic
- Enables external plugins and application components to observe story state changes
- Decouples story logic from application concerns (UI updates, external services, analytics)

**Behavior:**
- Filters actions by pattern (e.g., only `core/*` actions, or all actions)
- Publishes an `ActionDispatched` message containing: `session_id`, `action_type`, `payload`, `timestamp`
- Subscribers to the message bus can react without coupling to the action system

**Example use cases:**
- UI plugin listens for `core/end-game` to show ending cinematic
- External service plugin listens for custom actions to call APIs (e.g., image generation)
- Analytics plugin tracks all actions for player behavior analysis

```python
@dataclass(frozen=True)
class ActionDispatched(BaseMessage):
    session_id: UUID
    action_type: str  # e.g., "graph/transition", "core/end-game"
    payload: JsonValue
    timestamp: datetime
```

### Subscribing to `ActionDispatched`

Plugins and application components observe story actions by subscribing to `ActionDispatched` on the application's `MessageBus` — no coupling to the action system required:

```python
from llm_gamebook.story.state import ActionDispatched


def on_action_dispatched(message: ActionDispatched) -> None:
    print(f"{message.session_id}: {message.action_type} {message.payload}")


bus.subscribe(ActionDispatched, on_action_dispatched)
```

**Frontend delivery.** The game UI is one of these subscribers: the per-connection `WebSocketHandler` subscribes to `ActionDispatched` and forwards every published message as an `action_dispatched` server message over the app-wide WebSocket connection. The frontend fans received messages out to per-session subscribers by `sessionId`, and the `useActionDispatched(sessionId)` hook exposes the latest typed event for a session. The WebSocket layer performs **no filtering** — the publisher middleware's filter patterns are the only filtering control point, so what a session's client receives is exactly what the bound publisher published.

**End-game listener example** — a UI plugin that shows the ending when the game ends:

```python
from llm_gamebook.story.state import ActionDispatched


def show_ending(message: ActionDispatched) -> None:
    reason = message.payload.get("reason") if isinstance(message.payload, dict) else None
    ui.show_ending_cinematic(session_id=message.session_id, reason=reason)


bus.subscribe(ActionDispatched, show_ending)
```

**Notes for plugin authors:**

- **Async handlers require a running event loop.** `MessageBus` schedules async handlers as `asyncio` tasks. Engine dispatches happen inside the running loop (agent steps), so async handlers work there; if you subscribe for code paths outside a running loop, use sync handlers.
- **Subscribers must be robust.** A failing *sync* handler raises through `bus.publish` and aborts the dispatch that triggered it (pre-existing `MessageBus` semantics). Log and continue instead of re-raising. Async handler failures are isolated to their task and logged by the bus.
- Handlers see the message at dispatch time — *before* reducers apply the state change. `ActionDispatched` deliberately carries no state; query the session state later if you need the post-action view.

This unidirectional bridge (actions → message bus) is sufficient. The action system remains the authority over story state; no reverse communication is needed.

### History

Full snapshots after each agent step:
- Serialized state is attached to database `Part` model (when a state change has happened).
- It's possible to look at/restore previous states by walking back the previous messages.
- This makes it possible to "fork" sessions.

## Persistence

Session state is a simple dict of entity field overrides:

```json
{
  "entities": {
    "main": {"current_node_id": "unlock_ending"},
    "locations": {"current_node_id": "village"}
  }
}
```

Load: Project definition (YAML) + Session state (JSON) = Full state

## State Schema

The state schema are dynamic Pydantic models that are build from the static entity fields of the project definition.

### Data Types

We support simple data types:
- string
- number
- boolean
- entity reference (pointing to the ID of another entity)

### Data Migration

If the project definition changes:

- new fields get defaults
- removed fields are dropped
- static fields that became static are removed from state
- static fields that had a type change (e.g. 'string' -> 'number') are either cast and in error case initialized from default

## Trigger System

Triggers defined in YAML on entities:

```yaml
triggers:
  - name: graph/transition
    condition: =player.has_visited('village')
    args:
      to: unlock_ending
```

Evaluated after each agent step. Condition is a boolean expression. Action dispatched when condition is true.

## Message Bus Bridge

The action system and message bus are independent systems with different purposes:

| | Message Bus | Action System |
|--|-------------|---------------|
| **Intent** | Notify (pub/sub) | Transform state |
| **Pattern** | Fire and forget | Dispatch → Middleware → Reducer |
| **Scope** | Application-wide | Session-scoped |
| **Returns** | Nothing | New state |

**MessageBusPublisher** bridges them. It sits in the action system's middleware chain and publishes to the message bus, enabling:

- Gives the LLM means to publish events to the application logic
- External plugins to observe story actions without coupling to the action system
- Application components to react to story events (UI updates, service calls, analytics)
- A clean separation: actions are for state, message bus is for communication

The bridge is unidirectional (actions → message bus). This is sufficient because the action system is the authority over story state — external components only observe, never mutate.
