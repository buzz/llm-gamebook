## MODIFIED Requirements

### Requirement: Built-in middleware
The system SHALL provide built-in middleware: Logger, MessageBusPublisher, TriggerEval (stub), AutoSave (stub).

#### Scenario: Logger middleware
- **GIVEN** Logger middleware is configured
- **WHEN** an action is dispatched
- **THEN** the action details SHALL be logged

#### Scenario: MessageBusPublisher publishes when bound
- **GIVEN** a MessageBusPublisher middleware configured with a message bus and session ID
- **WHEN** an action is dispatched
- **THEN** an `ActionDispatched` message SHALL be published to the message bus

#### Scenario: MessageBusPublisher is a no-op when unbound
- **GIVEN** a MessageBusPublisher middleware configured without a message bus or without a session ID
- **WHEN** an action is dispatched
- **THEN** it SHALL pass the action through unchanged without publishing (behavior specified in the `message-bus-bridge` capability)

#### Scenario: TriggerEval middleware is a stub
- **GIVEN** TriggerEval middleware is configured
- **WHEN** an action is dispatched
- **THEN** it SHALL pass the action through without evaluation (Stage 4 feature)

#### Scenario: AutoSave middleware is a stub
- **GIVEN** AutoSave middleware is configured
- **WHEN** an action is dispatched
- **THEN** it SHALL pass the action through without saving (Stage 3/5 feature)
