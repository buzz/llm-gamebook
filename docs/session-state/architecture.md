# Session State Architecture

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

### Dynamic Fields

Any field can be:
- **Static**: literal value in YAML
- **Dynamic**: expression prefixed with `=`, evaluated at runtime

```yaml
entities:
  - id: main
    current_node_id: start           # static
    current_node_id: =other_entity.x # dynamic
```

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
