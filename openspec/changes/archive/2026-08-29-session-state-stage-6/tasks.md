> **Coordination:** `session-state-stage-4` (parallel) replaces the `trigger_eval` stub and `session-state-stage-5` touches `StoryContext`/engine wiring. This change owns the middleware chain assembly — recommended to implement **after Stage 4 lands**. Keep the `middleware.py` diff limited to the publisher function.

## 1. ActionDispatched Message

- [x] 1.1 Create `story/state/messages.py` with frozen `ActionDispatched(BaseMessage)`: `session_id: UUID`, `action_type: str`, `payload: JsonValue`, `timestamp: datetime` (UTC)
- [x] 1.2 Export `ActionDispatched` from `story/state/__init__.py`
- [x] 1.3 Add unit test: field roundtrip, immutability (frozen), importable from `llm_gamebook.story.state`

## 2. Publisher Middleware

- [x] 2.1 Implement `message_bus_publisher_middleware(bus, session_id, filter_pattern=None)` factory in `story/state/middleware.py`, replacing the stub (keep the `Middleware` callable shape)
- [x] 2.2 Return a pass-through no-op middleware when `bus` or `session_id` is `None`
- [x] 2.3 Publish `ActionDispatched` with `action_type = action.name`, `payload = action.payload.model_dump(mode="json")`, `timestamp = datetime.now(timezone.utc)`
- [x] 2.4 Implement fnmatch-style glob filtering (`str` or `list[str]`); `None` publishes all; filtered-out actions still reach reducers
- [x] 2.5 Add unit tests: fields match action, publish-before-reducer ordering, additional middleware dispatches also publish, UTC timestamp, no-filter/namespace/list filters, no-op without bus, no-op without session ID, multiple subscribers

## 3. Chain Assembly and Wiring

- [x] 3.1 Add optional `session_id: UUID | None` and `message_bus: MessageBus | None` params to `StoryContext.__init__`
- [x] 3.2 Assemble the default middleware chain in `StoryContext`: Logger → MessageBusPublisher → TriggerEval (stub) → AutoSave (stub); pass it to `Store` (extract a `default_middleware(bus, session_id)` helper in `middleware.py` if it keeps the constructor readable)
- [x] 3.3 Update `EngineManager._create_model_and_context` to pass the session ID and the application `MessageBus` into `StoryContext`
- [x] 3.4 Add unit tests: chain order observed, chain executes without bus (publisher no-op), existing `StoryContext` constructions still work (optional params)

## 4. Integration

- [x] 4.1 Add integration test: engine dispatch during an agent step publishes `ActionDispatched` on the application bus with correct `session_id`/`action_type`/`payload`
- [x] 4.2 Verify no regression in existing store/middleware tests (run `backend/tests/llm_gamebook/story/state/`)

## 5. Documentation

- [x] 5.1 Update `docs/session-state/steps-overview.md`: stage 6 row → `session-state-stage-6` / in-progress; remove "Message bus bridge (Stage 6)" from the not-implemented list
- [x] 5.2 Document plugin subscription to `ActionDispatched` in `docs/session-state/architecture.md` (subscribe code sample, end-game listener example, note on async handlers requiring a running event loop, robust-subscriber guidance)

## 6. Verification

- [x] 6.1 `ruff check backend/` and `ruff format --check backend/`
- [x] 6.2 `mypy backend/`
- [x] 6.3 `pytest backend/` full suite green
