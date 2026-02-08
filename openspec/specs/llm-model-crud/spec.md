## ADDED Requirements

### Requirement: Create LLM Model
The system SHALL allow users to create a new model configuration with provider, model name, and optional API credentials.

#### Scenario: User creates OpenAI model
- **WHEN** user fills the model form with:
  - Name: "OpenAI GPT-4o"
  - Provider: "openai"
  - Model Name: "gpt-4o"
  - Base URL: "https://api.openai.com/v1"
  - API Key: "sk-..."
- **THEN** system creates a new model configuration in the database
- **THEN** system returns the created model with generated UUID

#### Scenario: User creates Ollama model
- **WHEN** user fills the model form with:
  - Name: "Local Llama 3"
  - Provider: "ollama"
  - Model Name: "llama3"
  - Base URL: "http://localhost:11434"
  - API Key: (empty)
- **THEN** system creates a new model configuration
- **THEN** system returns the created model

#### Scenario: User creates model with advanced settings
- **WHEN** user fills the model form and expands "Advanced Settings"
- **THEN** user can edit JSON configuration with provider-specific options
- **WHEN** user saves the form
- **THEN** system stores the JSON configuration in settings_json field
- **THEN** system returns the created model with advanced settings

**Note:** JSONB settings_json field has been removed from implementation. All configuration is stored as direct columns.

### Requirement: List LLM Models
The system SHALL return a list of all configured LLM models ordered by creation date.

#### Scenario: User views model list
- **WHEN** user opens the "Models" section in the navbar
- **THEN** system displays all configured models
- **THEN** each model entry shows: name, provider, model name, edit/delete actions

#### Scenario: Empty model list
- **WHEN** user opens the "Models" section and no models exist
- **THEN** system displays empty state with "Create your first model" message
- **THEN** system shows "Add Model" button

### Requirement: Get Single LLM Model
The system SHALL return a single LLM model configuration by ID.

#### Scenario: User views model details
- **WHEN** user clicks on a model in the list
- **THEN** system returns the full model configuration including all fields
- **THEN** system does not return API key in response (security)

#### Scenario: Invalid model ID
- **WHEN** user requests a model with non-existent UUID
- **THEN** system returns 404 Not Found error
- **THEN** system returns error message: "Model not found"

### Requirement: Update LLM Model
The system SHALL allow users to modify an existing LLM model configuration.

#### Scenario: User updates model name
- **WHEN** user edits a model and changes the display name
- **THEN** system updates the name field in database
- **THEN** system returns updated model

#### Scenario: User updates API key
- **WHEN** user edits a model and provides new API key
- **THEN** system updates the api_key field in database
- **THEN** system returns updated model

#### Scenario: User updates provider
- **WHEN** user changes provider from OpenAI to Ollama
- **THEN** system validates new provider configuration
- **THEN** system updates all provider-related fields
- **THEN** system returns updated model

### Requirement: Delete Model
The system SHALL allow users to delete an LLM model configuration.

#### Scenario: User deletes model
- **WHEN** user clicks "Delete" on a model
- **THEN** system shows confirmation dialog
- **WHEN** user confirms deletion
- **THEN** system removes the model from database
- **THEN** system returns 204 No Content

#### Scenario: User cancels deletion
- **WHEN** user clicks "Delete" then clicks "Cancel"
- **THEN** system does not delete the model
- **THEN** model remains in the list

#### Scenario: Delete model with active sessions
- **WHEN** user deletes a model that is used by active sessions
- **THEN** system deletes the model
- **THEN** affected sessions fall back to default model or show error
- **THEN** system returns 204 No Content (no blocking)

### Requirement: Validate Model Configuration
The system SHALL validate model configurations according to provider requirements.

#### Scenario: Missing required base URL
- **WHEN** user creates a model without base URL for Ollama provider
- **THEN** system returns validation error: "Base URL is required for Ollama"
- **THEN** system does not create the model

#### Scenario: Invalid provider
- **WHEN** user specifies a provider not in the supported list
- **THEN** system returns validation error: "Provider not supported"
- **THEN** system does not create the model

#### Scenario: Invalid JSON in advanced settings
- **WHEN** user provides invalid JSON in advanced settings
- **THEN** system returns validation error: "Invalid JSON format"
- **THEN** system does not create the model

**Note:** JSONB settings_json field has been removed from implementation. All configuration is stored as direct columns.
