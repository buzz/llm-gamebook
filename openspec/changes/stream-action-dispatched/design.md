# Design: stream-action-dispatched

## Context

Stage 6 (merged) makes every dispatched story action observable as an `ActionDispatched` message on the application `MessageBus`, published by the `MessageBusPublisher` middleware before reducers apply the state change. Its proposal explicitly deferred *"delivering ActionDispatched over WebSocket to the frontend (separate follow-up change)"* — that is this change.

Current transport architecture:

- The frontend keeps **one app-wide WebSocket connection** (`/ws`), managed by `WebSocketContext` (`react-use-websocket`). The backend `WebSocketHandler` is a `BusSubscriber` created per connection; it forwards **all** sessions' engine bus messages as JSON messages from the `WebSocketServerMessage` discriminated union (`kind: Literal[...]`, camelCase aliases, schemas in `web/schemas/websocket/message.py`).
- The frontend context fans each received message out to **per-session subscribers** by `sessionId`; a hook (`useWebSocketConnection`) switches on `message.kind` with an `assertNever` exhaustiveness check.
- Frontend types for all WS messages are **generated from the OpenAPI schema** (`pnpm generate-api-types`); adding a member to the `WebSocketServerMessage` union propagates to the frontend automatically.
- `MessageBus.publish` runs async handlers as isolated tasks; a failing handler is logged via the done-callback and does not affect other subscribers. `WebSocketHandler._send_message` already no-ops (with a warning) when the socket is not connected.

## Goals / Non-Goals

**Goals:**
- Deliver every published `ActionDispatched` message to the connected WebSocket client as a first-class, typed server message
- Expose per-session, typed action events to frontend consumers following the existing event-hook pattern
- Keep the bus-level publisher filter patterns (Stage 6) the single filtering control point

**Non-Goals:**
- No filtering or sub-selection at the WebSocket layer (no per-connection allow/deny lists)
- No change to the connection model (no per-session sockets, no session query params)
- No frontend UI features built on the events (end-game banners, transition effects — later changes)
- No delivery of full state snapshots (action payloads only; state history stays in the DB/REST domain)
- No client-side event persistence or replay

## Decisions

### D1: Reuse the app-wide connection; no session scoping in the backend
The handler forwards `ActionDispatched` for **all** sessions, exactly like the existing engine messages; the message's `session_id` field and the frontend's existing `sessionId` fan-out handle routing.
*Alternative considered:* per-session sockets or a session filter in the handler. *Rejected:* breaks the established single-connection architecture and the connection URL (a breaking frontend change) for no benefit — the fan-out already exists and works.

### D2: New discriminated-union member `kind: "action_dispatched"`
`WebSocketActionDispatchedMessage` extends `BaseSessionWebSocketMessage` with `action_type: str`, `payload: JsonValue`, `timestamp: datetime` (UTC), mirroring `ActionDispatched`'s fields.
*Alternatives considered:*
- a generic `event` envelope with a type field — rejected: loses the generated type-safety that `assertNever` + OpenAPI types give the frontend;
- a per-action-type union member (one schema per action) — rejected: violates open/closed; every new action would force a WS schema change. The payload stays a JSON value (frontend type: `unknown`/`JsonValue`) because action payloads are schemaless on the wire by design; consumers interpret per `action_type`.

### D3: No filtering at the WebSocket layer
All published `ActionDispatched` messages are forwarded. Filtering stays where Stage 6 put it: the publisher's glob filter patterns.
*Alternative considered:* a default denylist for high-frequency actions (e.g. `graph/transition`). *Rejected:* keeps the socket a faithful mirror of the bus, avoids a second, divergent filtering control point, and the payloads are small (action payloads, not state snapshots). If churn ever becomes a problem, configure the publisher.

### D4: Frontend exposure via a dedicated typed hook
New hook (e.g. `useActionDispatched(sessionId)`) built on the context's existing `subscribe(sessionId, callback)`, returning the latest `WebSocketActionDispatchedMessage` (latest-only, no buffer — consistent with the existing stream hooks). `useWebSocketConnection`'s kind switch gains the `action_dispatched` case to satisfy exhaustiveness.
*Alternative considered:* raw `subscribe` in each consuming component — rejected: untyped and duplicates wiring per consumer.

### D5: Ordering semantics
Events are delivered in bus-publish order (publish happens before reducers apply the state change). There is **no ordering guarantee relative to stream messages** of the step that caused the action; consumers must treat action events as independent signals.

## Risks / Trade-offs

- **Event churn** (e.g. `graph/transition` on every node hop) → socket chatter. Mitigation: publisher filter patterns exist for this; monitor in practice; the WS layer deliberately does not add its own filter (D3).
- **Failing forward must not disturb the bus** → mitigated by existing isolation: async handlers run as isolated tasks (errors logged, not raised), `_send_message` no-ops when disconnected, and the handler's `close()` unsubscribes on disconnect.
- **No backward-compat window** → the frontend is in-repo and `assertNever` forces handling of the new kind in the same change; no stale-client risk in this deployment model.

## Migration Plan

No data migration. Backend and frontend deploy together (single repo); the union member is additive, so rollback is a plain revert.

## Open Questions

(none — D1–D5 cover the decisions raised during scoping)
