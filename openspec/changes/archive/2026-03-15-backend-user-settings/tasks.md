## 1. Database Model

- [x] 1.1 Create `UserSettings` model in `backend/llm_gamebook/db/models/user_settings.py`
- [x] 1.2 Add `UserSettings` to `backend/llm_gamebook/db/models/__init__.py` exports
- [x] 1.3 Create database table using SQLModel (auto-create on first access)

## 2. API Endpoints

- [x] 2.1 Create `backend/llm_gamebook/web/api/settings_router.py` with GET/PUT endpoints
- [x] 2.2 Add settings router to API router in `backend/llm_gamebook/web/api/api_router.py`
- [x] 2.3 Implement GET `/settings` endpoint with default creation logic
- [x] 2.4 Implement PUT `/settings` endpoint for updates
- [x] 2.5 No authentication dependency needed (single-user system)

## 3. API Schemas

- [x] 3.1 Create `UserSettings` schema in `backend/llm_gamebook/web/schemas/user_settings.py`
- [x] 3.2 Create `UserSettingsUpdate` schema for PUT requests
- [x] 3.3 Add schemas to `backend/llm_gamebook/web/schemas/__init__.py`

## 4. Testing

- [x] 4.1 Add unit tests for `UserSettings` model
- [x] 4.2 Add integration tests for settings API endpoints
- [x] 4.3 Test default settings creation on first access
- [x] 4.4 Test authentication requirements
