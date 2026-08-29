## Why

Stages 1-3 delivered session state and a Redux-inspired action system, but story actions are invisible outside the store: nothing bridges the action system to the application's message bus. External plugins and application components (UI, analytics, external services) have no way to observe story events like `core/end-game` or `graph/transition` without coupling to the action system. Stage 6 replaces the Stage 2 `MessageBusPublisher` stub with a functional middleware so every dispatched action becomes observable as an `ActionDispatched` bus message.

## What Changes

- New `ActionDispatched` message type (`session_id`, `action_type`, `payload`, `timestamp`) in a new domain-scoped module `story/state/messages.py`, following the `engine/message.py` pattern
- Replace the `message_bus_publisher_middleware` stub with a functional middleware: publishes `ActionDispatched` to the message bus when an action is dispatched (before reducers apply state), with optional glob filter patterns (e.g., `core/*`); no-op passthrough when no bus or session is bound
- Thread `session_id` and `MessageBus` through the `StoryContext` constructor (both optional, defaulting to no publishing)
- Assemble the default middleware chain in `StoryContext`: Logger → MessageBusPublisher → TriggerEval (stub until Stage 4) → AutoSave (stub). The chain is currently unwired — built-in middleware exists but is never passed to `Store`
- Update `EngineManager` to pass the application `MessageBus` and session ID into `StoryContext`
- Document plugin subscription to `ActionDispatched` (including an end-game listener example)

Out of scope: delivering `ActionDispatched` over WebSocket to the frontend (separate follow-up change).

## Capabilities

### New Capabilities

- `message-bus-bridge`: Action → message bus bridge — the `ActionDispatched` message, the `MessageBusPublisher` middleware with filter patterns, default middleware chain assembly, and the plugin subscription contract

### Modified Capabilities

- `action-system`: the "Built-in middleware" requirement changes — `MessageBusPublisher` becomes a functional built-in middleware and the default chain order (Logger → MessageBusPublisher → TriggerEval → AutoSave) is specified

## Impact

- **`story/state/middleware.py`**: stub replaced by functional publisher middleware (factory form)
- **`story/state/messages.py`** (new): `ActionDispatched` message class
- **`story/state/__init__.py`**: export `ActionDispatched`
- **`story/context.py`**: new optional constructor params (`session_id`, `message_bus`) + middleware chain assembly
- **`engine/manager.py`**: pass bus and session ID when creating `StoryContext`
- **Specs**: new `message-bus-bridge` capability; `action-system` "Built-in middleware" requirement updated
- **Docs**: `docs/session-state/steps-overview.md` stage table; subscription documentation
- **Coordination**: `session-state-stage-4` (in parallel) fills in the TriggerEval stub and must not restructure the chain — this change owns chain assembly. Recommended to implement Stage 6 after Stage 4 lands to avoid the shared `middleware.py`/`StoryContext` seam
