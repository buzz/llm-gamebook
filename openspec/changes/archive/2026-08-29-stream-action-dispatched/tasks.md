## 1. WebSocket Message Schema (backend)

- [x] 1.1 Add `WebSocketActionDispatchedMessage` to `web/schemas/websocket/message.py`: extends `BaseSessionWebSocketMessage`, `kind: Literal["action_dispatched"]`, fields `action_type: str`, `payload: JsonValue`, `timestamp: datetime` (UTC)
- [x] 1.2 Add `from_message(ActionDispatched)` classmethod mapping the bus message to the WS message (follow the `WebSocketStreamMessageMessage.from_message` pattern)
- [x] 1.3 Add the new message to the `WebSocketServerMessage` discriminated union

## 2. Handler Forwarding (backend)

- [x] 2.1 Subscribe `WebSocketHandler` to `ActionDispatched` (bus subscription in `__init__`, handler `_on_action_dispatched`)
- [x] 2.2 Forward every published message via `_send_message` — no filtering at the WS layer (publisher filter patterns remain the control point)
- [x] 2.3 Verify disconnect behavior: `close()` on connection end removes the subscription (no send attempts after disconnect)
- [x] 2.4 Make `MessageBus` thread-aware (added during implementation): capture the event loop; when `publish` is called from a thread without a running loop (pydantic-ai runs sync tools in an executor thread), schedule async handlers on the captured loop via `call_soon_threadsafe`; when no loop was captured or it is closed, log an error and skip async handlers instead of raising
- [x] 2.5 Unit: `publish` from a worker thread delivers to async subscribers on the captured loop; `publish` with no captured loop raises no exception

## 3. Backend Tests

- [x] 3.1 Unit: `from_message` field mapping (session_id, action_type, payload, timestamp) and camelCase serialization
- [x] 3.2 Unit: handler forwards actions of any type (no WS-level filtering); when the publisher filter excludes an action at the bus level, nothing is delivered for it
- [x] 3.3 Unit: forwarding failure (disconnected socket) raises no exception and does not propagate into the bus publish path; other `ActionDispatched` subscribers still receive the message
- [x] 3.4 Integration: action dispatched during an agent step is delivered over the WebSocket with correct `kind`, `session_id`, `action_type`, `payload`, `timestamp` (extend the broken-bulb fixtures if feasible, otherwise FastAPI `TestClient` websocket)

## 4. Frontend

- [x] 4.1 Regenerate OpenAPI types (`pnpm generate-api-types`, requires backend running at localhost:8000)
- [x] 4.2 Export `WebSocketActionDispatchedMessage` from `types/websocket.ts`; handle the `action_dispatched` kind in `useWebSocketConnection`'s switch (satisfy `assertNever` exhaustiveness)
- [x] 4.3 Add typed hook `useActionDispatched(sessionId)` on top of `WebSocketContext.subscribe`, exposing the latest event for the session
- [x] 4.4 Vitest: hook exposes the latest event for the session and is not invoked for other sessions' events

## 5. Documentation

- [x] 5.1 Update `docs/session-state/architecture.md` subscription section: note frontend delivery over the app-wide WebSocket, per-session fan-out by `sessionId`, and that publisher filter patterns are the only filtering control point

## 6. Verification

- [x] 6.1 `ruff check backend/` and `ruff format --check backend/`
- [x] 6.2 `mypy backend/`
- [x] 6.3 `pytest backend/` full suite green
- [x] 6.4 `pnpm lint`, `pnpm typecheck`, `pnpm test`
- [x] 6.5 `openspec validate stream-action-dispatched`
