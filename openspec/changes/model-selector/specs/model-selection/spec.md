## ADDED Requirements

### Requirement: Select Model for Session
The system SHALL allow users to select which model configuration to use for their game session.

#### Scenario: User changes model mid-session
- **WHEN** user selects a different model from the model selector dropdown
- **THEN** system updates the session's current model association
- **THEN** subsequent messages use the newly selected model
- **THEN** system returns confirmation of model change

#### Scenario: Session restores with last used model
- **WHEN** user reopens a saved session
- **THEN** session loads with the last used model selected
- **THEN** new messages use the restored model

#### Scenario: User views available models
- **WHEN** user opens the model selector in a session
- **THEN** system displays all configured models
- **THEN** system highlights the currently active model
- **THEN** system shows provider icon/name next to each model

### Requirement: Default Model Fallback
The system SHALL use a default model when no specific model is selected.

#### Scenario: New session without model selection
- **WHEN** user creates a new session
- **THEN** system assigns the first available model as default
- **THEN** system uses this model for all messages until user changes it

#### Scenario: Selected model deleted
- **WHEN** user deletes the model currently associated with a session
- **THEN** session falls back to the first available model
- **THEN** new messages use the fallback model

### Requirement: Model Selection UI
The system SHALL provide a visual model selector component in the session interface.

#### Scenario: Model selector displays current model
- **WHEN** user is in a session
- **THEN** system displays the currently selected model name
- **THEN** system shows provider icon/color indicator
- **THEN** system provides dropdown to change model

#### Scenario: Model selector shows model information
- **WHEN** user hovers over a model in the dropdown
- **THEN** system displays model details: provider, model name
- **THEN** system shows any configured advanced settings summary

#### Scenario: Loading state during model switch
- **WHEN** user selects a different model
- **THEN** system shows loading indicator
- **THEN** system disables further model changes until switch completes
- **THEN** system displays error if model switch fails

### Requirement: Model Request Logging
The system SHALL log which model was used for each message in a session.

#### Scenario: Message uses selected model
- **WHEN** user sends a message
- **THEN** system records the model ID used for that request
- **THEN** system stores the model ID with the message for audit

#### Scenario: Model configuration stored with message
- **WHEN** message is sent with a model
- **THEN** system captures model configuration snapshot
- **THEN** snapshot stored to ensure reproducibility if model config changes

**Note:** The database schema uses direct columns (provider, model_name, base_url, api_key) instead of JSONB settings_json.
