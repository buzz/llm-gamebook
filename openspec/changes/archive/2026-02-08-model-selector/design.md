## Context

The current implementation uses hardcoded LLM models in `get_model_tmp.py`, requiring code changes to switch providers or models. The codebase uses Pydantic AI for LLM abstraction, which provides 32 providers and a consistent model interface.

**Current State:**
- Models hardcoded with fixed provider configuration
- No user-facing model management
- No provider flexibility

**Constraints:**
- Must use Pydantic AI's provider/model architecture
- Must integrate with existing FastAPI backend and React frontend
- API keys will be stored in plain text (local development tool)
- Must support future provider expansion without schema changes

**Stakeholders:**
- Backend: @llm-gamebook/backend
- Frontend: @llm-gamebook/frontend
- Users: Gamebook players who want to experiment with different models

## Goals / Non-Goals

**Goals:**
- Replace hardcoded model configuration with database-driven approach
- Provide CRUD API for LLM model configurations
- Build frontend UI for model management in navbar
- Support 6 initial providers: OpenAI, Ollama, Groq, DeepSeek, Mistral, OpenRouter
- Enable per-session model selection during gameplay
- Design schema flexible enough for all 32 Pydantic AI providers

**Non-Goals:**
- Dynamic provider discovery from Pydantic AI (hardcode list for v1)
- Full model name discovery (use free text, not /v1/models endpoint)
- API key encryption (plain text storage acceptable for local dev)
- All 32 providers support (start with 6, expand later)

## Decisions

### 1. Database Schema: JSONB for Provider-Specific Config

**Decision:** Use single `llm_model` table with JSONB `settings_json` field for provider-specific configuration.

**Rationale:**
- Single table simplifies queries and migrations
- JSONB provides flexibility for future providers with different config requirements
- Matches Pydantic AI's `ModelSettings` pattern
- Easy to add validation layer later without schema changes

**Alternative Considered:** Separate tables per provider
- Rejected: Would require 32 tables, complex migrations, poor flexibility

**Alternative Considered:** EAV (Entity-Attribute-Value) pattern
- Rejected: Poor query performance, harder to reason about

### 2. Naming Convention: `ModelConfig` / `model_config`

**Decision:** Use `ModelConfig` class name and `model_config` file/module names to clearly indicate this stores configuration rather than being a "model" in the traditional sense.

**Rationale:**
- Clear distinction from SQLAlchemy/SQLModel base Model class
- Avoids naming collisions with existing entities
- Better semantic meaning: this is a configuration, not a model instance
- Frontend components already use `ModelConfig` terminology (ModelConfigSelector, ModelConfigLink)

### 3. Database Schema: Direct Fields vs JSONB

**Decision:** Use direct columns for all configuration fields instead of JSONB.

**Rationale:**
- Simpler queries and indexing
- Easier validation at database level
- Provider list is hardcoded anyway (not dynamic)
- Matches implementation: provider, model_name, base_url, api_key as direct fields
- No need for complex JSON parsing

**Alternative Considered:** JSONB `settings_json` field
- Rejected: Overly complex for this use case
- **Note:** All traces of JSONB settings have been removed from the implementation

**Decision:** Hardcode 8 providers for v1: Anthropic, DeepSeek, Google, Mistral, Ollama, OpenAI, OpenRouter, xAI.

**Rationale:**
- Most commonly used providers
- Reduces implementation scope for v1
- Can add more providers incrementally
- Pydantic AI doesn't expose provider list programmatically

**Alternative:** Dynamic discovery via `pydantic_ai.providers` module inspection
- Rejected: Complex, may include unstable/internal providers, overkill for v1

### 4. API Key Storage

**Decision:** Store API keys in plain text in database.

**Rationale:**
- Local development tool, not production SaaS
- Simplicity over security for MVP
- Form field masks input for user experience
- Can add encryption layer later if needed

**Risk:** Local machine compromise exposes API keys
**Mitigation:** Document this limitation, users responsible for security

### 5. Model Selection: Per-Session, Not Global

**Decision:** Each session tracks its current model. Model can be switched per user input.

**Rationale:**
- Enables experimentation during gameplay
- Matches proposal requirement: "model can be switched freely on each user input"
- Session restoration selects last used model

### 6. Frontend Architecture

**Decision:** Add "Models" section to left sidebar in Navbar.

**Rationale:**
- Matches existing navigation pattern (Gamebooks section)
- Easy access without navigating away from current context
- Clear hierarchy: Gamebooks → Models

**Alternative:** Separate settings page
- Rejected: Less convenient for quick model switches during gameplay

### 7. Model Form Design

**Decision:** Single form with:
- Name (user-friendly display name)
- Provider (dropdown from 8 providers)
- Model Name (free text)
- Base URL (pre-filled but editable)
- API Key (masked input)

**Rationale:**
- Simple for common case (OpenAI defaults)
- Single form reduces UI complexity
- No JSON advanced settings needed

**Alternative:** Provider-specific forms
- Rejected: 8 forms to maintain, hard to add new providers

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Provider validation complexity | Runtime errors if required config missing | Add validation layer, clear error messages |
| Missing provider features | Some provider-specific options not exposed | Accept limitations, expand providers as needed |
| API key exposure | Local dev machine compromise | Document limitation, consider encryption v2 |

## Migration Plan

1. **Create database table** - Add `model_config` table with migration
2. **Seed default models** - Optional: pre-populate common configurations
3. **Build backend API** - CRUD endpoints for model_config
4. **Build frontend UI** - Navbar section + form components
5. **Update get_model** - Replace hardcoded path with DB lookup
6. **Test flow** - Verify model selection in gameplay session

**Rollback:** Revert to `get_model_tmp.py` hardcoded path if issues arise.

## Open Questions

1. **Provider-specific validation**: Should we validate required fields per provider at save time?
   - Example: OpenAI requires base_url, Anthropic requires api_key
   - Recommendation: Yes, add validation layer

2. **Default model**: Should there be a system-wide default model?
   - Currently not in scope, but useful for new sessions
   - Defer to v2

3. **Model name validation**: Should we validate model names exist?
   - Pydantic AI doesn't validate model names at configuration time
   - Validation happens at request time
   - Accept this limitation for v1

4. **Connection pooling**: How to handle provider client lifecycle?
   - Pydantic AI manages this internally
   - Each model request creates client as needed
   - Accept current behavior
