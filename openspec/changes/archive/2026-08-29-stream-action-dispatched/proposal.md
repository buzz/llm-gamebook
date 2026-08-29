## Why

Stage 6 bridged the story action system to the application message bus (`ActionDispatched`), but explicitly deferred delivering those events over WebSocket to the frontend. Today, dispatched story actions (e.g. `core/end-game`, `graph/transition`) are only observable in-process: the game UI cannot react to story events without polling or reaching into backend state. This change completes the bridge by streaming `ActionDispatched` events to the already-connected per-session WebSocket.

## What Changes

- New `WebSocketActionDispatchedMessage` server message (`kind: "action_dispatched"`, `session_id`, `action_type`, `payload`, `timestamp`) added to the `WebSocketServerMessage` discriminated union, following the existing `BaseSessionWebSocketMessage` pattern
- `WebSocketHandler` subscribes to `ActionDispatched` on the application bus and forwards the messages of its connected session to the client socket
- No new filtering at the WebSocket layer: all `ActionDispatched` messages published for the session are forwarded (the bus-level publisher filter patterns remain the control)
- Frontend: regenerate OpenAPI types; handle the new message kind in the WebSocket hook (the `assertNever` exhaustiveness check requires it); expose dispatched action events to consumers following the existing stream-event hook pattern
- Docs: note frontend delivery in `docs/session-state/architecture.md` (subscription section)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `message-bus-bridge`: add requirements for frontend delivery — the WebSocket handler SHALL forward the connected session's published `ActionDispatched` messages as `action_dispatched` server messages, and the frontend SHALL expose those events to application consumers

## Impact

- **Backend**: `web/schemas/websocket/message.py` (new message type + union member), `web/websocket/handler.py` (bus subscription + forwarding), `message_bus/message_bus.py` (thread-aware publish: async handlers are schedulable from non-loop threads, e.g. pydantic-ai tool executor threads — required because tool-driven dispatches publish `ActionDispatched` off-loop)
- **Frontend**: `types/websocket.ts` (regenerated), `hooks/websocket.ts` (new kind handling), consumer hook + tests (Vitest/RTL)
- **API types**: `pnpm generate-api-types` after the backend union change
- **Docs**: `docs/session-state/architecture.md`
- No breaking changes; existing server messages and clients are unaffected
