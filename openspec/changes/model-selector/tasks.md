## 1. Database

- [x] 1.1 Create `backend/llm_gamebook/db/models/model_config.py` with SQLModel `ModelConfig` table
- [x] 1.2 Add `model_config` table to database migration (Alembic or SQLModel create_all)
- [x] 1.3 Add provider list constant (Anthropic, DeepSeek, Google, Mistral, Ollama, OpenAI, OpenRouter, xAI)

## 2. Backend API - Pydantic Schemas

- [x] 2.1 Create `backend/llm_gamebook/web/schemas/model_config.py` with request/response models
- [x] 2.2 Define `ModelConfigCreate` schema with validation
- [x] 2.3 Define `ModelConfigUpdate` schema
- [x] 2.4 Define `ModelConfigResponse` schema (exclude api_key)
- [x] 2.5 Add provider-specific validation logic

## 3. Backend API - CRUD Endpoints

- [x] 3.1 Create `backend/llm_gamebook/web/api/model_config/crud.py` with:
  - `create_model_config()`
  - `get_model_configs()`
  - `get_model_config()`
  - `update_model_config()`
  - `delete_model_config()`
- [x] 3.2 Create `backend/llm_gamebook/web/api/model_config/router.py` with endpoints:
  - `POST /model-configs/` - Create model
  - `GET /model-configs/` - List models
  - `GET /model-configs/{id}` - Get single model
  - `PUT /model-configs/{id}` - Update model
  - `DELETE /model-configs/{id}` - Delete model
- [x] 3.3 Register router in `backend/llm_gamebook/web/api/router.py`

## 4. Backend Engine - Model Factory

- [x] 4.1 Create `backend/llm_gamebook/web/model_factory.py` with factory function
- [x] 4.2 Implement `create_model_from_db_config()` function
- [x] 4.3 Add provider-specific provider instantiation (AnthropicProvider, DeepSeekProvider, GoogleProvider, MistralProvider, OllamaProvider, OpenAIProvider, OpenRouterProvider, XaiProvider)
- [x] 4.5 Update `get_model.py` to use factory function

## 5. Frontend - API Types

- [x] 5.1 Run `pnpm generate-api-types` to generate TypeScript interfaces
- [x] 5.2 Verify generated types in `frontend/src/types/openapi.d.ts`

## 6. Frontend - RTK Query Service

- [x] 6.1 Create `frontend/src/services/modelConfig.ts` with RTK Query endpoints
- [x] 6.2 Define `useGetModelConfigsQuery` hook
- [x] 6.3 Define `useGetModelConfigQuery` hook
- [x] 6.4 Define `useCreateModelConfigMutation` hook
- [x] 6.5 Define `useUpdateModelConfigMutation` hook
- [x] 6.6 Define `useDeleteModelConfigMutation` hook

## 7. Frontend - Model Form Component

- [x] 7.1 Create `frontend/src/components/ModelConfigForm.tsx`
- [x] 7.2 Implement provider dropdown with 8 providers
- [x] 7.3 Implement model name field (free text)
- [x] 7.4 Implement base URL field with provider-specific pre-fill
- [x] 7.5 Implement API key field with masking
- [x] 7.7 Add form validation and error handling
- [x] 7.8 Connect form to RTK Query mutations

## 8. Frontend - Navbar Models Section

- [x] 8.1 Update `frontend/src/components/layout/Navbar.tsx` to add "Models" section
- [x] 8.2 Add "Models" nav item with icon
- [x] 8.3 Add model list display under Models section
- [x] 8.4 Add "Create new model" button
- [x] 8.5 Add edit/delete actions per model
- [x] 8.6 Implement empty state when no models exist

## 9. Frontend - Model Selector in Session

- [x] 9.1 Create `frontend/src/components/ModelConfigSelector.tsx`
- [x] 9.2 Add model selector dropdown to session view
- [x] 9.3 Display current model with provider indicator
- [x] 9.4 Connect selector to session state management
- [x] 9.5 Handle model switch with loading state
- [x] 9.6 Implement fallback to first available model

## 10. Testing

- [x] 10.1 Write backend tests for CRUD endpoints (`tests/api/test_model_config.py`)
- [x] 10.2 Write backend tests for model factory (`tests/web/test_model_factory.py`)
- [ ] 10.3 Write frontend tests for ModelConfigForm component
- [ ] 10.4 Write frontend tests for ModelConfigSelector component
- [x] 10.5 Run backend lint and typecheck (`uv run ruff check`, `uv run mypy`)
- [x] 10.6 Run frontend lint and typecheck (`pnpm lint`, `pnpm typecheck`)

## 11. Integration

- [ ] 11.1 Connect session message sending to use selected model
- [ ] 11.2 Update session model association on model switch
- [ ] 11.3 Add model ID to message logging for audit
- [ ] 11.4 Test end-to-end flow: create model → select in session → send message
