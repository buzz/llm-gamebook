# State History

## Purpose

This capability enables the system to keep a history of session state snapshots so a game can support save games, undo, and session branching. It stores complete state snapshots with agent responses, walks message history to find previous states, and provides the core game actions restore, fork, end-game, and reset-game, with cleanup to bound history growth.

## Requirements

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

### Requirement: Restore endpoint
The system SHALL expose `POST /api/sessions/{session_id}/restore` accepting `{"step": int}` (0-based message index, `-1` for the latest state) that restores the session to the state of the most recent snapshot at or before the target step. Restore is soft time-travel: later messages are NOT removed from the session history.

#### Scenario: Restore to a specific step
- **GIVEN** a session whose messages include state snapshots at steps 2, 5, and 7
- **WHEN** `POST /api/sessions/{session_id}/restore` is called with `{"step": 4}`
- **THEN** the response SHALL be 200
- **AND** the session's current state SHALL become the snapshot stored at step 2
- **AND** messages after step 4 SHALL remain in the session history

#### Scenario: Restore to latest
- **GIVEN** a session with at least one state snapshot
- **WHEN** `POST /api/sessions/{session_id}/restore` is called with `{"step": -1}`
- **THEN** the response SHALL be 200
- **AND** the session's current state SHALL become the most recent snapshot

#### Scenario: Restore with no snapshots
- **GIVEN** a session with no messages carrying state
- **WHEN** `POST /api/sessions/{session_id}/restore` is called with any valid step
- **THEN** the response SHALL be 200
- **AND** the session's current state SHALL be the empty state (project defaults)

#### Scenario: Restore with invalid step
- **GIVEN** a session with 6 messages
- **WHEN** `POST /api/sessions/{session_id}/restore` is called with `{"step": 6}` or `{"step": -2}`
- **THEN** the response SHALL be 422

#### Scenario: Restore on nonexistent session
- **WHEN** `POST /api/sessions/{session_id}/restore` is called for a session that does not exist
- **THEN** the response SHALL be 404

#### Scenario: Restore on an ended session
- **GIVEN** a session marked as ended with at least one state snapshot
- **WHEN** `POST /api/sessions/{session_id}/restore` is called with a valid step
- **THEN** the response SHALL be 200 and the state SHALL be restored
- **AND** the session SHALL remain marked as ended (no further agent responses allowed)

### Requirement: Fork endpoint
The system SHALL expose `POST /api/sessions/{session_id}/fork` accepting `{"step": int}` that creates a new independent session with the state of the most recent snapshot at or before the target step. The message history of the source session SHALL NOT be copied.

#### Scenario: Fork from a historical step
- **GIVEN** a session with state snapshots at steps 2, 5, and 7
- **WHEN** `POST /api/sessions/{session_id}/fork` is called with `{"step": 6}`
- **THEN** the response SHALL be 201 and contain the new session
- **AND** the new session SHALL use the same project as the source
- **AND** the new session's state SHALL equal the snapshot stored at step 5
- **AND** the new session SHALL have no message history
- **AND** the source session SHALL be unchanged (state, messages, ended status)

#### Scenario: Fork from latest
- **GIVEN** a session with at least one state snapshot
- **WHEN** `POST /api/sessions/{session_id}/fork` is called with `{"step": -1}`
- **THEN** the new session's state SHALL equal the most recent snapshot

#### Scenario: Fork with no state available
- **GIVEN** a session with no messages carrying state
- **WHEN** `POST /api/sessions/{session_id}/fork` is called
- **THEN** the response SHALL be 409

#### Scenario: Fork with invalid step
- **GIVEN** a session with 6 messages
- **WHEN** `POST /api/sessions/{session_id}/fork` is called with `{"step": 6}` or `{"step": -2}`
- **THEN** the response SHALL be 422

### Requirement: End-game endpoint
The system SHALL expose `POST /api/sessions/{session_id}/end-game` accepting an optional `{"reason": string}` body that marks the session as ended. The endpoint SHALL be idempotent.

#### Scenario: End an active session
- **GIVEN** an active (not ended) session
- **WHEN** `POST /api/sessions/{session_id}/end-game` is called
- **THEN** the response SHALL be 200
- **AND** the session SHALL be marked as ended with a timestamp
- **AND** no further agent responses SHALL be generated for the session

#### Scenario: End with a reason
- **GIVEN** an active session
- **WHEN** `POST /api/sessions/{session_id}/end-game` is called with `{"reason": "reached the ending"}`
- **THEN** the response SHALL be 200
- **AND** the session SHALL be marked as ended

#### Scenario: End an already-ended session
- **GIVEN** a session already marked as ended
- **WHEN** `POST /api/sessions/{session_id}/end-game` is called
- **THEN** the response SHALL be 200
- **AND** the session's ended status SHALL be unchanged

### Requirement: Reset endpoint
The system SHALL expose `POST /api/sessions/{session_id}/reset` that clears the session state back to project defaults. Reset SHALL also un-end the session. The message history SHALL be preserved.

#### Scenario: Reset an active session
- **GIVEN** a session with modified entity fields
- **WHEN** `POST /api/sessions/{session_id}/reset` is called
- **THEN** the response SHALL be 200
- **AND** the session's state SHALL be cleared so all fields fall back to project defaults
- **AND** the message history SHALL be preserved

#### Scenario: Reset an ended session
- **GIVEN** a session marked as ended
- **WHEN** `POST /api/sessions/{session_id}/reset` is called
- **THEN** the response SHALL be 200
- **AND** the session SHALL no longer be marked as ended
- **AND** the session SHALL be playable again

### Requirement: State history listing
The system SHALL expose `GET /api/sessions/{session_id}/states` that lists all stored state snapshots of a session in ascending step order. Each entry SHALL contain the step number (0-based message index), the snapshot's timestamp, and the number of entity fields changed in that snapshot.

#### Scenario: List snapshots
- **GIVEN** a session with state snapshots at steps 2, 5, and 7
- **WHEN** `GET /api/sessions/{session_id}/states` is called
- **THEN** the response SHALL be 200
- **AND** the listing SHALL contain exactly 3 entries in ascending step order: 2, 5, 7
- **AND** each entry SHALL carry the corresponding message timestamp and field count

#### Scenario: List snapshots of a new session
- **GIVEN** a session with no messages carrying state
- **WHEN** `GET /api/sessions/{session_id}/states` is called
- **THEN** the response SHALL be 200 with an empty listing

#### Scenario: List snapshots of a nonexistent session
- **WHEN** `GET /api/sessions/{session_id}/states` is called for a session that does not exist
- **THEN** the response SHALL be 404

### Requirement: Session API exposes ended state
The session API response models (`Session` and `SessionFull`) SHALL include an `endedAt` timestamp field: `null` for active sessions and the end timestamp for ended sessions.

#### Scenario: Active session response
- **GIVEN** an active session
- **WHEN** any session read endpoint returns it
- **THEN** the response SHALL include `endedAt: null`

#### Scenario: Ended session response
- **GIVEN** a session marked as ended
- **WHEN** any session read endpoint returns it
- **THEN** the response SHALL include `endedAt` set to the end timestamp
