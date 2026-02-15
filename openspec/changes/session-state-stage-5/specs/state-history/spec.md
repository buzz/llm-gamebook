## ADDED Requirements

### Requirement: Full state stored with each response
The system SHALL store complete session state (not just deltas) with each agent response message.

#### Scenario: State stored on response
- **GIVEN** an agent step completes with state changes
- **WHEN** the response is saved
- **THEN** the complete state SHALL be serialized and stored in the message's state field

#### Scenario: State matches expected after step
- **GIVEN** a session at step N
- **WHEN** the state is retrieved from message N
- **THEN** it SHALL match the effective state after step N

### Requirement: State traversal finds previous states
The system SHALL provide functionality to walk back through message history to find previous states.

#### Scenario: Traverse to find state
- **GIVEN** a session with multiple messages
- **WHEN** searching for state at step N
- **THEN** the system SHALL walk messages from oldest to newest
- **AND** return the state from the most recent message with non-null state at or before step N

#### Scenario: Handle gaps in state
- **GIVEN** messages where some responses have no state (no changes occurred)
- **WHEN** searching for state
- **THEN** the system SHALL continue walking back until a message with state is found

#### Scenario: No previous state exists
- **GIVEN** a new session with no messages or no messages with state
- **WHEN** searching for previous state
- **THEN** return None or empty state

### Requirement: Restore action returns to previous state
The system SHALL provide a core/restore action that restores session to a previous point.

#### Scenario: Restore to point
- **GIVEN** a session at step N with state
- **WHEN** core/restore action is dispatched with target step M (where M < N)
- **THEN** the current state SHALL become the state from step M

#### Scenario: Restore to latest
- **GIVEN** a session with multiple states
- **WHEN** core/restore action is dispatched without target (or target = -1)
- **THEN** restore to the most recent previous state

### Requirement: Fork creates independent branch
The system SHALL support forking from any historical state, creating an independent session.

#### Scenario: Fork from historical state
- **GIVEN** a session at step N
- **WHEN** core/fork action is dispatched with target step M
- **THEN** a new session SHALL be created
- **AND** the new session SHALL have the state from step M
- **AND** the original session SHALL be unchanged

#### Scenario: Fork is independent
- **GIVEN** a forked session
- **WHEN** actions are taken in the fork
- **THEN** they SHALL NOT affect the original session

### Requirement: End-game action
The system SHALL provide a core/end-game action that marks the session as ended.

#### Scenario: End game action
- **GIVEN** an active session
- **WHEN** core/end-game action is dispatched
- **THEN** the session SHALL be marked as ended
- **AND** no further agent responses SHALL be generated

### Requirement: Reset-game action
The system SHALL provide a core/reset-game action that clears state and restarts from defaults.

#### Scenario: Reset game action
- **GIVEN** a session with state
- **WHEN** core/reset-game action is dispatched
- **THEN** all session state SHALL be cleared
- **AND** the session SHALL restart from project defaults

### Requirement: State history cleanup
The system SHALL limit stored state history to prevent unbounded growth.

#### Scenario: Cleanup old snapshots
- **GIVEN** a session with more than N stored states (configurable limit)
- **WHEN** a new state is stored
- **THEN** the oldest states beyond the limit SHALL be removed

#### Scenario: Latest states preserved
- **GIVEN** a session approaching history limit
- **WHEN** cleanup occurs
- **THEN** the most recent states SHALL be preserved
- **AND** only older states beyond the limit SHALL be removed
