# Delta Spec: session-history-ui

## ADDED Requirements

### Requirement: Game lifecycle toolbar controls
The player view SHALL provide a "Game" toolbar group exposing the session lifecycle controls: Undo, state history, Fork, End game, and Reset. Controls SHALL reflect availability: history-dependent controls are disabled when the session has no stored snapshots, End game is disabled when the session is already ended, and Reset is always available for an existing session.

#### Scenario: Controls visible in player view
- **GIVEN** a player with a session that has stored state snapshots
- **WHEN** the player view is rendered
- **THEN** the toolbar SHALL show Undo, a History control, Fork, End game, and Reset

#### Scenario: History-dependent controls without snapshots
- **GIVEN** a player with a session that has no stored state snapshots
- **WHEN** the player view is rendered
- **THEN** Undo, the History control, and Fork SHALL be disabled

#### Scenario: End game disabled when already ended
- **GIVEN** a player with a session marked as ended
- **WHEN** the player view is rendered
- **THEN** the End game control SHALL be disabled

#### Scenario: Reset requires confirmation
- **GIVEN** a player with a session
- **WHEN** the player triggers Reset
- **THEN** a confirmation dialog SHALL be shown before any API call
- **AND** only after confirmation SHALL the reset request be sent
- **AND** canceling SHALL leave the session unchanged

### Requirement: State history menu
The player view SHALL provide a state history listing showing each stored snapshot with its step number and timestamp. Selecting an entry restores the session to that snapshot ("continue from here"). After a successful restore, the view SHALL refresh to reflect the restored state.

#### Scenario: History listing
- **GIVEN** a session with state snapshots at steps 2, 5, and 7
- **WHEN** the player opens the state history
- **THEN** the listing SHALL show the three snapshots in ascending step order with their timestamps

#### Scenario: Restore from the history
- **GIVEN** an open state history listing
- **WHEN** the player selects the snapshot at step 5
- **THEN** a restore request SHALL be sent for step 5
- **AND** on success the view SHALL refresh to reflect the restored state

#### Scenario: Undo restores the previous snapshot
- **GIVEN** a session whose newest snapshots are at steps 5 and 7
- **WHEN** the player triggers Undo
- **THEN** a restore request SHALL be sent for step 5

#### Scenario: Empty history
- **GIVEN** a session with no stored state snapshots
- **WHEN** the player opens the state history
- **THEN** the history SHALL indicate that no snapshots exist

### Requirement: Fork navigates to the new session
When the player forks a session, the player view SHALL navigate to the newly created session after a successful fork.

#### Scenario: Fork and navigate
- **GIVEN** a player in session A with stored state snapshots
- **WHEN** the player forks from the current state
- **THEN** a fork request SHALL be sent for the latest state
- **AND** on success the player view SHALL switch to the new session (new session ID, same project)
- **AND** the original session SHALL be untouched and still reachable

### Requirement: Ended session display
When a session is marked as ended, the player view SHALL display an ended banner and disable the input area and the request/send action so no further user requests can be sent.

#### Scenario: Ended session shown
- **GIVEN** a session whose API response has `endedAt` set
- **WHEN** the player view is rendered for that session
- **THEN** an ended banner SHALL be shown
- **AND** the input area and the send action SHALL be disabled

#### Scenario: Active session unaffected
- **GIVEN** a session whose API response has `endedAt: null`
- **WHEN** the player view is rendered for that session
- **THEN** no ended banner SHALL be shown
- **AND** the input area and send action SHALL remain enabled

### Requirement: History limit setting exposed
The settings form SHALL expose a control for the `maxStateHistory` user setting (default 50) that is persisted via the existing user settings API.

#### Scenario: Default value shown
- **GIVEN** a user with default settings
- **WHEN** the settings form is rendered
- **THEN** the history limit control SHALL show 50

#### Scenario: Persisting a new value
- **GIVEN** the settings form with the history limit set to 100
- **WHEN** the user saves the settings
- **THEN** the updated value SHALL be persisted via the user settings API
- **AND** the form SHALL reflect the saved value
