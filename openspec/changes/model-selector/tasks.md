## 1. Database

- [ ] 1.1 Create `backend/llm_gamebook/db/models/llm_model.py` with SQLModel `LLMModel` table
- [ ] 1.2 Add `llm_model` table to database migration (Alembic or SQLModel create_all)
- [ ] 1.3 Add provider list constant (OpenAI, Ollama, Groq, DeepSeek, Mistral, OpenRouter)

## 2. Backend API - Pydantic Schemas

- [ ] 2.1 Create `backend/llm_gamebook/web/api/llm_models/schemas.py` with request/response models
- [ ] 2.2 Define `LLMModelCreate` schema with validation
- [ ] 2.3 Define `LLMModelUpdate` schema
- [ ] 2.4 Define `LLMModelResponse` schema (exclude api_key)
- [ ] 2.5 Add provider-specific validation logic

## 3. Backend API - CRUD Endpoints

- [ ] 3.1 Create `backend/llm_gamebook/web/api/llm_models/crud.py` with:
  - `create_llm_model()`
  - `get_llm_models()`
  - `get_llm_model()`
  - `update_llm_model()`
  - `delete_llm_model()`
- [ ] 3.2 Create `backend/llm_gamebook/web/api/llm_models/router.py` with endpoints:
  - `POST /llm-models/` - Create model
  - `GET /llm-models/` - List models
  - `GET /llm-models/{id}` - Get single model
  - `PUT /llm-models/{id}` - Update model
  - `DELETE /llm-models/{id}` - Delete model
- [ ] 3.3 Register router in `backend/llm_gamebook/web/api/router.py`

## 4. Backend Engine - Model Factory

- [ ] 4.1 Create `backend/llm_gamebook/engine/llm_model_factory.py` with factory function
- [ ] 4.2 Implement `create_model_from_db_config()` function
- [ ] 4.3 Add provider-specific provider instantiation (OpenAIProvider, OllamaProvider, etc.)
- [ ] 4.4 Handle settings_json deserialization for provider-specific options
- [ ] 4.5 Update `get_model_tmp.py` to use factory function (or create new get_llm_model.py)

## 5. Frontend - API Types

- [ ] 5.1 Run `pnpm generate-api-types` to generate TypeScript interfaces
- [ ] 5.2 Verify generated types in `frontend/src/types/openapi.d.ts`

## 6. Frontend - RTK Query Service

- [ ] 6.1 Create `frontend/src/services/llmModels.ts` with RTK Query endpoints
- [ ] 6.2 Define `useGetLlmModelsQuery` hook
- [ ] 6.3 Define `useGetLlmModelQuery` hook
- [ ] 6.4 Define `useCreateLlmModelMutation` hook
- [ ] 6.5 Define `useUpdateLlmModelMutation` hook
- [ ] 6.6 Define `useDeleteLlmModelMutation` hook

## 7. Frontend - Model Form Component

- [ ] 7.1 Create `frontend/src/components/LLMModelForm.tsx`
- [ ] 7.2 Implement provider dropdown with 6 providers
- [ ] 7.3 Implement model name field (free text)
- [ ] 7.4 Implement base URL field with provider-specific pre-fill
- [ ] 7.5 Implement API key field with masking
- [ ] 7.6 Implement advanced settings JSON editor (toggle)
- [ ] 7.7 Add form validation and error handling
- [ ] 7.8 Connect form to RTK Query mutations

## 8. Frontend - Navbar Models Section

- [ ] 8.1 Update `frontend/src/components/layout/Navbar.tsx` to add "Models" section
- [ ] 8.2 Add "Models" nav item with icon
- [ ] 8.3 Add model list display under Models section
- [ ] 8.4 Add "Create new model" button
- [ ] 8.5 Add edit/delete actions per model
- [ ] 8.6 Implement empty state when no models exist

## 9. Frontend - Model Selector in Session

- [ ] 9.1 Create `frontend/src/components/ModelSelector.tsx`
- [ ] 9.2 Add model selector dropdown to session view
- [ ] 9.3 Display current model with provider indicator
- [ ] 9.4 Connect selector to session state management
- [ ] 9.5 Handle model switch with loading state
- [ ] 9.6 Implement fallback to first available model

## 10. Testing

- [ ] 10.1 Write backend tests for CRUD endpoints (`tests/api/test_llm_models.py`)
- [ ] 10.2 Write backend tests for model factory (`tests/engine/test_llm_model_factory.py`)
- [ ] 10.3 Write frontend tests for ModelForm component
- [ ] 10.4 Write frontend tests for ModelSelector component
- [ ] 10.5 Run backend lint and typecheck (`uv run ruff check`, `uv run mypy`)
- [ ] 10.6 Run frontend lint and typecheck (`pnpm lint`, `pnpm typecheck`)

## 11. Integration

- [ ] 11.1 Connect session message sending to use selected model
- [ ] 11.2 Update session model association on model switch
- [ ] 11.3 Add model ID to message logging for audit
- [ ] 11.4 Test end-to-end flow: create model → select in session → send message
