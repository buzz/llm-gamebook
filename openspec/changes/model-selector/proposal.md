## Why

Currently, the LLM model selection is hardcoded in `get_model_tmp.py`, requiring code changes to switch models or providers. Users need a UI to configure, select, and manage LLM models without touching code. This enables flexible model experimentation and provider switching during gameplay.

## What Changes

- New database table `model_config` for storing provider configurations
- CRUD API endpoints for managing model configurations (`/api/model-configs/`)
- Frontend model management UI in navbar with create/edit/delete forms
- Backend factory function to create Pydantic AI models from database config
- Support for 8 common providers: Anthropic, DeepSeek, Google, Mistral, Ollama, OpenAI, OpenRouter, xAI
- Session model association (per-session model selection, not global)

## Capabilities

### New Capabilities
- `model-config-crud`: API and UI for creating, reading, updating, and deleting model configuration
- `model-selection`: UI for selecting which model to use per conversation/session

### Modified Capabilities
- None (new capability)

## Impact

- **Backend**: New `model_config.py` SQLModel, CRUD operations, API endpoints, model factory
- **Frontend**: Navbar "Models" section, model form component, RTK Query services
- **Database**: New `model_config` table with direct provider fields (no JSONB)
- **Dependencies**: No new dependencies; uses existing Pydantic AI introspection
