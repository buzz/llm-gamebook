## 1. Database Model

- [ ] 1.1 Create `UserSettings` model in `backend/llm_gamebook/db/models/user_settings.py`
- [ ] 1.2 Add `UserSettings` to `backend/llm_gamebook/db/models/__init__.py` exports
- [ ] 1.3 Create database table using SQLModel (auto-create on first access)

## 2. API Endpoints

- [ ] 2.1 Create `backend/llm_gamebook/web/api/settings_router.py` with GET/PUT endpoints
- [ ] 2.2 Add settings router to API router in `backend/llm_gamebook/web/api/api_router.py`
- [ ] 2.3 Implement GET `/settings` endpoint with default creation logic
- [ ] 2.4 Implement PUT `/settings` endpoint for updates
- [ ] 2.5 No authentication dependency needed (single-user system)

## 3. API Schemas

- [ ] 3.1 Create `UserSettings` schema in `backend/llm_gamebook/web/schemas/user_settings.py`
- [ ] 3.2 Create `UserSettingsUpdate` schema for PUT requests
- [ ] 3.3 Add schemas to `backend/llm_gamebook/web/schemas/__init__.py`

## 4. Testing

- [ ] 4.1 Add unit tests for `UserSettings` model
- [ ] 4.2 Add integration tests for settings API endpoints
- [ ] 4.3 Test default settings creation on first access
- [ ] 4.4 Test authentication requirements
