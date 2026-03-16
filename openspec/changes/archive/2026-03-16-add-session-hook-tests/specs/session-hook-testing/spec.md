## ADDED Requirements

### Requirement: useCreateSession hook creates new session and navigates
The `useCreateSession` hook SHALL create a new session via the session API and navigate to the player view on success.

#### Scenario: Successful session creation
- **WHEN** `createSession(projectId, modelConfigId)` is called
- **AND** the API call succeeds
- **THEN** the system SHALL navigate to the player view route with the new session ID
- **AND** no error notification SHALL be shown

#### Scenario: Failed session creation
- **WHEN** `createSession(projectId, modelConfigId)` is called
- **AND** the API call fails
- **THEN** an error notification SHALL be shown with message "Failed to create story session!"
- **AND** no navigation SHALL occur

#### Scenario: Session creation loading state
- **WHEN** the hook is called
- **THEN** `isLoading` SHALL be `true` while the API call is in progress
- **AND** `isLoading` SHALL be `false` after the call completes (success or failure)

### Requirement: useDeleteSession hook deletes session with confirmation
The `useDeleteSession` hook SHALL request confirmation before deleting a session and handle navigation appropriately.

#### Scenario: Successful deletion with confirmation
- **WHEN** `deleteSession(session)` is called
- **AND** the user confirms the deletion in the modal
- **AND** the API call succeeds
- **THEN** the session SHALL be deleted
- **AND** a success notification SHALL be shown with message "Story session was deleted."
- **AND** no navigation SHALL occur if the current location is not the player view

#### Scenario: Deletion cancelled by user
- **WHEN** `deleteSession(session)` is called
- **AND** the user cancels the deletion in the modal
- **THEN** the API SHALL NOT be called
- **AND** no navigation SHALL occur
- **AND** no notifications SHALL be shown

#### Scenario: Failed deletion
- **WHEN** `deleteSession(session)` is called
- **AND** the user confirms the deletion
- **AND** the API call fails
- **THEN** an error notification SHALL be shown with message "Failed to delete story session!"
- **AND** no navigation SHALL occur

#### Scenario: Deleting active session navigates to home
- **WHEN** `deleteSession(session)` is called
- **AND** the current location is the player view for that session
- **AND** the user confirms the deletion
- **AND** the API call succeeds
- **THEN** the system SHALL navigate to the home page
- **AND** a success notification SHALL be shown

### Requirement: Session hooks expose loading state
Both `useCreateSession` and `useDeleteSession` hooks SHALL expose an `isLoading` property reflecting the API call state.

#### Scenario: useCreateSession exposes isLoading
- **WHEN** the `useCreateSession` hook is called
- **THEN** it SHALL return an object with `isLoading` property
- **AND** `isLoading` SHALL be a boolean value

#### Scenario: useDeleteSession exposes isLoading
- **WHEN** the `useDeleteSession` hook is called
- **THEN** it SHALL return an object with `isLoading` property
- **AND** `isLoading` SHALL be a boolean value
