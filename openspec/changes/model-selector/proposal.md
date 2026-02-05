## Why

Currently, the LLM model selection is hardcoded in `get_model_tmp.py`, requiring code changes to switch models or providers. Users need a UI to configure, select, and manage LLM models without touching code. This enables flexible model experimentation and provider switching during gameplay.

## What Changes

- New database table `llm_model` for storing provider configurations
- CRUD API endpoints for managing LLM models (`/api/llm-models/`)
- Frontend model management UI in navbar with create/edit/delete forms
- Backend factory function to create Pydantic AI models from database config
- Support for 6 common providers initially: OpenAI, Ollama, Groq, DeepSeek, Mistral, OpenRouter
- Session model association (per-session model selection, not global)

## Capabilities

### New Capabilities
- `llm-model-crud`: API and UI for creating, reading, updating, and deleting LLM model configurations
- `model-selection`: UI for selecting which model to use per conversation/session

### Modified Capabilities
- None (new capability)

## Impact

- **Backend**: New `llm_model.py` SQLModel, CRUD operations, API endpoints, model factory
- **Frontend**: Navbar "Models" section, model form component, RTK Query services
- **Database**: New `llm_model` table with JSONB for provider-specific settings
- **Dependencies**: No new dependencies; uses existing Pydantic AI introspection
