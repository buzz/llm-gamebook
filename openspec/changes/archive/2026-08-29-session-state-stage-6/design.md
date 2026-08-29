## Context

Stages 1-3 (session state, action system, action-driven changes) are complete. The current state of the relevant code:

- `Store` accepts a `middleware: list[Middleware]` chain (`type Middleware = Callable[[Store, Action[BaseModel]], Action[BaseModel]]`) and runs it before reducers. `MAX_DISPATCH_DEPTH = 2` allows middleware to dispatch one additional action that itself re-enters the chain.
- `story/state/middleware.py` defines four built-ins: `logging_middleware` (functional), `message_bus_publisher_middleware` (stub, "Stage 6"), `trigger_eval_middleware` (stub, "Stage 4"), `auto_save_middleware` (stub).
- **The chain is unwired**: `StoryContext.__init__` constructs `Store(initial_state)` with no middleware, so none of the built-ins run in production paths.
- The message bus is mature: `MessageBus` (sync `publish`, async handlers spawned as tasks, `wait_all`), `BusSubscriber` (weakref-tracked subscriptions), and `BaseMessage` (frozen dataclass). Concrete message types live in domain-scoped modules (`engine/message.py`), not in `message_bus/messages.py` (which holds only `BaseMessage` + the handler type alias).
- `session_id` is known to `EngineManager` (it constructs `StoryEngine(session_id, model, context, bus)`) but is absent from `StoryContext` and `Store`.
- **Parallel changes in flight**: `session-state-stage-4` (triggers — replaces the `trigger_eval` stub; task 5.1 touches middleware chain order) and `session-state-stage-5` (history, core actions). Both are at 0 tasks completed.

## Goals / Non-Goals

**Goals:**
- `ActionDispatched` message type carrying `session_id`, `action_type`, `payload`, `timestamp`
- Functional `MessageBusPublisher` middleware: publishes after dispatch, before reducers; optional glob filter patterns; safe no-op when unbound
- `session_id` + `MessageBus` threaded through `StoryContext`
- Default middleware chain assembled in `StoryContext`: Logger → MessageBusPublisher → TriggerEval → AutoSave
- `EngineManager` passes the app bus and session ID into `StoryContext`
- Subscription documentation for plugins (end-game listener example)

**Non-Goals:**
- WebSocket/frontend delivery of `ActionDispatched` (follow-up change)
- Reverse communication (message bus → action system) — the bridge is unidirectional by design
- Changes to `Store` dispatch semantics, reducer composition, or `SessionState`
- Making TriggerEval or AutoSave functional (Stage 4 / later stages)
- Changing `MessageBus` publish/subscribe semantics

## Decisions

### 1. `ActionDispatched` lives in `story/state/messages.py`

**Decision:** New module `backend/llm_gamebook/story/state/messages.py` holding `ActionDispatched`, mirroring the `engine/message.py` pattern. Exported from `story/state/__init__.py`.

**Rationale:** Concrete messages are domain-scoped in this codebase. `message_bus/messages.py` holds only `BaseMessage` and the `MessageHandler` type alias — moving story action messages there would invert that boundary.

**Alternatives considered:**
- `message_bus/messages.py`: Rejected — that module is the framework base, not a domain message home.
- `engine/message.py`: Rejected — engine messages describe engine lifecycle; story actions belong to the story state domain.

### 2. `session_id` and `MessageBus` are optional `StoryContext` constructor params

**Decision:** `StoryContext(project, session_state_data=None, session_id: UUID | None = None, message_bus: MessageBus | None = None)`. The publisher middleware is created via a factory that closes over both; `Store`'s public signature is unchanged.

**Rationale:** Session binding is an application-level concern, not a store-level one — `Store` stays generic and unit-testable without app objects. `EngineManager` already holds both values at the construction site. Optional params keep every existing `StoryContext` construction (tests, TUI paths) working untouched.

**Alternatives considered:**
- `session_id` on `Store`: Rejected — pollutes a generic state container with app identity.
- `store.bind_session(session_id)` post-construction: Rejected — mutable, easily forgotten, and the window where it is unset is error-prone.
- Required params on `StoryContext`: Rejected — breaks parallel in-flight changes and existing tests; no publishing is the natural default for contexts built without a bus.

### 3. Publisher middleware is a factory, not a bare function

**Decision:** `message_bus_publisher_middleware(bus: MessageBus | None, session_id: UUID | None, filter_pattern: str | list[str] | None = None) -> Middleware`. If `bus` or `session_id` is `None`, the returned middleware is a pass-through no-op. `filter_pattern` is `fnmatch`-style glob(s) on `action.name`; `None` means publish everything.

**Adaptation (Stage 4 landed first):** Stage 4 refactored the middleware chain to the onion model — `Middleware` is now `Callable[[Store, Action[BaseModel], Next], SessionState]`. The factory keeps its signature and returns an onion middleware that publishes (when the filter matches) **before** calling `next_chain(action)`, preserving the before-reducers timing. The unbound pass-through simply calls `next_chain(action)`.

**Alternatives considered:**
- Config object on `Store`: Rejected — couples Store to bus configuration.
- Glob only (single `str`): Rejected at no cost — accepting `list[str]` covers "publish `core/*` and `graph/*`" cleanly.

### 4. Chain assembly is owned by this change, in `StoryContext.__init__`

**Decision:** `StoryContext` builds `middleware = [logging_middleware, publisher, trigger_eval_middleware(self), auto_save_middleware]` (fixed order per `docs/session-state/architecture.md`) and passes it to `Store`. The stub slots are wired in now; later stages replace the stub function bodies, never the assembly or the order.

**Adaptation (Stage 4 landed first):** Stage 4 already assembled this exact chain inline in `StoryContext.__init__`, with the publisher left as its (old-signature) stub. Stage 6 keeps that assembly and only replaces the bare stub entry with the bound factory call `message_bus_publisher_middleware(message_bus, session_id)`; no `default_middleware` helper was extracted, keeping the Stage 6 diff in `middleware.py` limited to the publisher function as coordinated.

### 5. Publish timing: inside the chain, before reducers

**Decision:** The publisher runs at its chain position (after Logger, before TriggerEval), so the `ActionDispatched` message is emitted after the action is dispatched but before reducers apply the state change — matching the architecture doc. In the onion chain this means publishing before calling `next_chain`. Actions that middleware dispatches additionally (e.g., Stage 4 trigger actions) re-enter the chain and are each published exactly once.

**Rationale:** Observers get a notification of *intent*; they never see intermediate reducer output, and the action system remains the authority over state. Per-dispatch publishing (no dedup) is correct: each dispatched action is a distinct event.

**Consequence:** A subscriber querying `store.get_state()` during a handler sees the pre-action state. `ActionDispatched` deliberately carries no state — only `session_id`, `action_type`, `payload`, `timestamp`.

### 6. Payload and timestamp construction

**Decision:** `action_type = action.name`; `payload = action.payload.model_dump(mode="json")` (a `JsonValue`); `timestamp = datetime.now(timezone.utc)`.

**Rationale:** `mode="json"` guarantees JSON-serializable values (datetimes → ISO strings, etc.), matching the documented `JsonValue` type. UTC avoids naive-timestamp ambiguity.

### 7. Error policy: no swallowing

**Decision:** The middleware performs no error handling around `bus.publish`. `MessageBus` already logs and (for sync handlers) re-raises handler failures; that semantics is unchanged.

**Rationale:** Swallowing publish errors would hide broken subscribers; the project standard forbids broad exception catching. The no-bus case is handled structurally (no-op middleware), not via exceptions.

## Risks / Trade-offs

- [Parallel-change seam: S4/S5 edit `middleware.py` and `StoryContext` concurrently] → This change owns chain assembly; S4 replaces only the `trigger_eval` function body, S5 avoids the constructor. Recommended sequencing: land Stage 4 first, then Stage 6. Keep the Stage 6 diff in `middleware.py` limited to the publisher function. **Outcome: Stage 4 landed into main before Stage 6 was implemented, as recommended. Stage 4 went further than anticipated (onion middleware refactor + chain assembly), so the publisher was adapted to the new `Middleware` signature and the pre-existing assembly was kept; see Decisions 3–4.
- [Sync dispatch vs async bus: `publish` spawns `asyncio.create_task` for async handlers, requiring a running loop] → Engine dispatch happens inside the running loop (agent step), which is the real path. Tests with a live bus + async handlers must be async tests. Sync-only subscribers work without a loop. Documented in the subscription guide.
- [A failing sync subscriber raises through `publish` and aborts the dispatch] → Pre-existing `MessageBus` semantics, not introduced here. Documented: subscribers must be robust (log and continue); the bus's async path already isolates failures to the task.
- [Wiring the chain activates `logging_middleware` (one INFO log per action)] → Acceptable default; volume can be controlled via the `llm_gamebook.story.state.middleware` logger level at runtime.
- [`ActionDispatched` not delivered to the frontend] → Deliberate non-goal; the WebSocket handler subscription pattern already exists and a follow-up change can forward the message without rework.

## Migration Plan

Purely additive; no database, API, or message-format changes. Rollback is a revert of the change. Suggested implementation order (after Stage 4 lands):

1. `ActionDispatched` + module + exports
2. Publisher middleware factory + unit tests
3. `StoryContext` params + chain assembly (+ `EngineManager` wiring)
4. Integration test (engine dispatch → bus receives `ActionDispatched`)
5. Docs (steps-overview table, subscription guide)

## Open Questions

- None blocking. The frontend delivery follow-up (WebSocket forwarding of `ActionDispatched`) is intentionally deferred and not named yet.
