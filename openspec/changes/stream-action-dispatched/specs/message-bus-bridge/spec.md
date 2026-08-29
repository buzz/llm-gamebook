# Delta Spec: message-bus-bridge

## ADDED Requirements

### Requirement: WebSocket delivers ActionDispatched to connected clients
The system SHALL deliver `ActionDispatched` messages published on the application message bus to the application's WebSocket as a server message with `kind` `action_dispatched`, carrying `session_id`, `action_type`, `payload`, and `timestamp`. The message SHALL be a member of the `WebSocketServerMessage` union. The WebSocket layer SHALL NOT filter action types: every published `ActionDispatched` message SHALL be forwarded, with filtering remaining the responsibility of the bus-level publisher filter patterns.

#### Scenario: Action dispatched during an agent step is delivered
- **GIVEN** a connected WebSocket client and an engine bound to the application bus for a session
- **WHEN** an action of type `graph/transition` is dispatched during an agent step
- **THEN** the client SHALL receive a server message with `kind` `action_dispatched`, `session_id` of the session, `action_type` `graph/transition`, the JSON-serialized action payload, and a UTC `timestamp`

#### Scenario: Publisher filter suppresses delivery
- **GIVEN** a publisher middleware configured with a filter pattern that excludes an action type
- **AND** a connected WebSocket client
- **WHEN** that excluded action is dispatched alongside an allowed action
- **THEN** the client SHALL NOT receive an `action_dispatched` message for the excluded action
- **AND** the client SHALL receive an `action_dispatched` message for the allowed action

#### Scenario: Forwarding failure does not disturb other subscribers
- **GIVEN** a connected client and another bus subscriber to `ActionDispatched`
- **WHEN** the WebSocket forwarding handler fails
- **THEN** the failure SHALL NOT prevent the other subscriber from receiving the message
- **AND** no exception SHALL propagate into the bus publish path

#### Scenario: Handler unsubscribes on disconnect
- **GIVEN** a WebSocket connection that is closed
- **WHEN** an action is dispatched afterwards
- **THEN** no send attempt SHALL be made on the closed connection

### Requirement: Frontend exposes dispatched action events
The frontend SHALL expose `action_dispatched` server messages to application consumers with typed, per-session access following the existing WebSocket event pattern, and SHALL handle the `action_dispatched` kind in its server-message type union (exhaustive kind handling).

#### Scenario: Session-scoped consumer receives events
- **GIVEN** a frontend component subscribed to action events for a session
- **WHEN** an `action_dispatched` message for that session is received
- **THEN** the consumer SHALL receive the typed message with `session_id`, `action_type`, `payload`, and `timestamp`

#### Scenario: Other sessions' events are not delivered
- **GIVEN** a consumer subscribed to action events for session A
- **WHEN** an `action_dispatched` message for session B is received
- **THEN** the consumer SHALL NOT be invoked for that message

#### Scenario: Latest event accessible per session
- **GIVEN** a frontend hook tracking action events for a session
- **WHEN** multiple `action_dispatched` messages for that session are received
- **THEN** the hook SHALL expose the most recently received message
