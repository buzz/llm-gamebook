# Message Bus Bridge

## Purpose

Bridges the story action system to the application message bus. Every dispatched story action is observable as an `ActionDispatched` message (session ID, action type, JSON-serialized payload, UTC timestamp) published by the MessageBusPublisher middleware before reducers apply the state change. Supports optional glob filter patterns, a safe no-op when no bus or session is bound, and is assembled in the default `StoryContext` middleware chain so plugins and application components can observe story events without coupling to the action system.

## Requirements


### Requirement: ActionDispatched message structure
The system SHALL provide an `ActionDispatched` message type, extending `BaseMessage` as a frozen dataclass, carrying: `session_id` (UUID), `action_type` (namespaced action name, e.g. `graph/transition`), `payload` (JSON-serializable value), and `timestamp` (timezone-aware UTC datetime).

#### Scenario: Message carries action details
- **GIVEN** an `ActionDispatched` constructed with a session ID, action type, payload, and timestamp
- **WHEN** its fields are read
- **THEN** `session_id`, `action_type`, `payload`, and `timestamp` SHALL be returned as provided
- **AND** the message SHALL be immutable (frozen)

#### Scenario: Message is importable by plugins
- **GIVEN** an external plugin that imports `ActionDispatched` from `llm_gamebook.story.state`
- **WHEN** the import is performed
- **THEN** the class SHALL be available without importing private modules

### Requirement: Publisher middleware publishes ActionDispatched on dispatch
The system SHALL provide a functional MessageBusPublisher middleware that publishes an `ActionDispatched` message to the bound message bus when an action is dispatched, before the action's reducers apply any state change.

#### Scenario: Message fields match the dispatched action
- **GIVEN** a store whose middleware chain includes a publisher bound to a bus and session ID
- **WHEN** an action with type `graph/transition` and a payload is dispatched
- **THEN** an `ActionDispatched` message SHALL be published with `action_type` equal to the action's name, `session_id` equal to the bound session ID, and `payload` equal to the JSON-serialized action payload

#### Scenario: Publish happens before state change
- **GIVEN** a subscriber that records the store state at the moment it receives `ActionDispatched`
- **WHEN** a state-changing action is dispatched
- **THEN** the recorded state SHALL not yet reflect the action's reducer effect

#### Scenario: Additional dispatches are also published
- **GIVEN** a middleware that dispatches an additional action while processing a dispatched action
- **WHEN** the original action is dispatched
- **THEN** an `ActionDispatched` message SHALL be published for the additional action as well

#### Scenario: Timestamp is UTC
- **GIVEN** any published `ActionDispatched` message
- **WHEN** its `timestamp` is inspected
- **THEN** it SHALL be a timezone-aware datetime in UTC

### Requirement: Filter patterns control which actions are published
The system SHALL support an optional glob filter pattern (single pattern or list of patterns) on the action name for the publisher middleware. When no pattern is set, all actions are published.

#### Scenario: No filter publishes all actions
- **GIVEN** a publisher middleware without a filter pattern
- **WHEN** actions of any type are dispatched
- **THEN** an `ActionDispatched` message SHALL be published for each

#### Scenario: Namespace filter
- **GIVEN** a publisher middleware with filter pattern `core/*`
- **WHEN** a `core/end-game` action and a `graph/transition` action are dispatched
- **THEN** a message SHALL be published for `core/end-game`
- **AND** no message SHALL be published for `graph/transition`

#### Scenario: Multiple filter patterns
- **GIVEN** a publisher middleware with filter patterns `core/*` and `graph/*`
- **WHEN** a `core/end-game` action and an `audio/play` action are dispatched
- **THEN** messages SHALL be published for `core/end-game`
- **AND** no message SHALL be published for `audio/play`

#### Scenario: Filtered action still processed
- **GIVEN** a publisher middleware whose filter excludes an action type
- **WHEN** that action is dispatched
- **THEN** its reducers SHALL still run and state SHALL change normally

### Requirement: Publisher is a no-op when unbound
The system SHALL make the publisher middleware a pass-through no-op (no publishing, no error, action reaches reducers unchanged) when it was created without a message bus or without a session ID.

#### Scenario: No message bus
- **GIVEN** a publisher middleware created without a message bus
- **WHEN** an action is dispatched
- **THEN** no message SHALL be published and no error SHALL be raised
- **AND** the action SHALL reach its reducers

#### Scenario: No session ID
- **GIVEN** a publisher middleware created with a bus but without a session ID
- **WHEN** an action is dispatched
- **THEN** no message SHALL be published and no error SHALL be raised

### Requirement: Multiple subscribers receive the same message
The system SHALL deliver each published `ActionDispatched` message to every subscriber registered for the message type, independent of the action system.

#### Scenario: Two subscribers both notified
- **GIVEN** two handlers subscribed to `ActionDispatched`
- **WHEN** an action is dispatched
- **THEN** both handlers SHALL receive the message

### Requirement: StoryContext assembles the default middleware chain
The system SHALL assemble the default middleware chain in `StoryContext` in the order Logger → MessageBusPublisher → TriggerEval → AutoSave, and SHALL pass it to the `Store`. The chain SHALL be assembled even when no bus or session ID is provided (with the publisher acting as a no-op).

#### Scenario: Chain order
- **GIVEN** a `StoryContext` created with a bus and session ID
- **WHEN** an action is dispatched
- **THEN** the middleware SHALL execute in the order Logger, MessageBusPublisher, TriggerEval, AutoSave

#### Scenario: Chain without bus
- **GIVEN** a `StoryContext` created without a bus or session ID
- **WHEN** an action is dispatched
- **THEN** the middleware chain SHALL still execute in the defined order
- **AND** the publisher SHALL contribute no messages

### Requirement: Engine manager binds contexts to the application bus
The system SHALL have the engine manager pass the application `MessageBus` and the session ID when creating a `StoryContext` for a session, so actions dispatched during agent steps are observable on the application bus.

#### Scenario: Engine action observable on app bus
- **GIVEN** a session whose engine was created with the application bus
- **WHEN** an action is dispatched during an agent step
- **THEN** an `ActionDispatched` message for that action SHALL be published on the application bus

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
