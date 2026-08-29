## 1. WebSocket Message Schema (backend)

- [ ] 1.1 Add `WebSocketActionDispatchedMessage` to `web/schemas/websocket/message.py`: extends `BaseSessionWebSocketMessage`, `kind: Literal["action_dispatched"]`, fields `action_type: str`, `payload: JsonValue`, `timestamp: datetime` (UTC)
- [ ] 1.2 Add `from_message(ActionDispatched)` classmethod mapping the bus message to the WS message (follow the `WebSocketStreamMessageMessage.from_message` pattern)
- [ ] 1.3 Add the new message to the `WebSocketServerMessage` discriminated union

## 2. Handler Forwarding (backend)

- [ ] 2.1 Subscribe `WebSocketHandler` to `ActionDispatched` (bus subscription in `__init__`, handler `_on_action_dispatched`)
- [ ] 2.2 Forward every published message via `_send_message` — no filtering at the WS layer (publisher filter patterns remain the control point)
- [ ] 2.3 Verify disconnect behavior: `close()` on connection end removes the subscription (no send attempts after disconnect)

## 3. Backend Tests

- [ ] 3.1 Unit: `from_message` field mapping (session_id, action_type, payload, timestamp) and camelCase serialization
- [ ] 3.2 Unit: handler forwards actions of any type (no WS-level filtering); when the publisher filter excludes an action at the bus level, nothing is delivered for it
- [ ] 3.3 Unit: forwarding failure (disconnected socket) raises no exception and does not propagate into the bus publish path; other `ActionDispatched` subscribers still receive the message
- [ ] 3.4 Integration: action dispatched during an agent step is delivered over the WebSocket with correct `kind`, `session_id`, `action_type`, `payload`, `timestamp` (extend the broken-bulb fixtures if feasible, otherwise FastAPI `TestClient` websocket)

## 4. Frontend

- [ ] 4.1 Regenerate OpenAPI types (`pnpm generate-api-types`, requires backend running at localhost:8000)
- [ ] 4.2 Export `WebSocketActionDispatchedMessage` from `types/websocket.ts`; handle the `action_dispatched` kind in `useWebSocketConnection`'s switch (satisfy `assertNever` exhaustiveness)
- [ ] 4.3 Add typed hook `useActionDispatched(sessionId)` on top of `WebSocketContext.subscribe`, exposing the latest event for the session
- [ ] 4.4 Vitest: hook exposes the latest event for the session and is not invoked for other sessions' events

## 5. Documentation

- [ ] 5.1 Update `docs/session-state/architecture.md` subscription section: note frontend delivery over the app-wide WebSocket, per-session fan-out by `sessionId`, and that publisher filter patterns are the only filtering control point

## 6. Verification

- [ ] 6.1 `ruff check backend/` and `ruff format --check backend/`
- [ ] 6.2 `mypy backend/`
- [ ] 6.3 `pytest backend/` full suite green
- [ ] 6.4 `pnpm lint`, `pnpm typecheck`, `pnpm test`
- [ ] 6.5 `openspec validate stream-action-dispatched`
