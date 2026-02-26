## 1. Backend Constants

- [x] 1.1 Add `STORIES_DIR` and `EXAMPLES_DIR` to `constants.py`
- [x] 1.2 Update `app.py` lifespan to create `STORIES_DIR` on startup

## 2. Story Discovery

- [x] 2.1 Create `backend/llm_gamebook/story_project/__init__.py`
- [x] 2.2 Create `story_project/schemas.py` with StorySource enum and Story response model
- [x] 2.3 Create `story_project/discovery.py` with `discover_stories()` function
- [x] 2.4 Implement discovery scanning for `examples/{namespace}/{story}/` directories
- [x] 2.5 Implement discovery scanning for `STORIES_DIR/{namespace}/{story}/` directories
- [x] 2.6 Derive story name from path: `{namespace}/{story}`

## 3. Story Manager

- [x] 3.1 Create `story_project/manager.py` with StoryManager class
- [x] 3.2 Implement `list_stories()` combining examples and user stories
- [x] 3.3 Implement `get_story(story_id)` for individual story lookup
- [x] 3.4 Implement `create_story(name, title)` creating directory + `llm-gamebook.yaml`

## 4. Story API Router

- [x] 4.1 Create `web/api/story_router.py` with `/api/stories` endpoints
- [x] 4.2 Implement `GET /api/stories` with optional source filter
- [x] 4.3 Implement `GET /api/stories/{id}` returning story details
- [x] 4.4 Implement `DELETE /api/stories/{id}` deleting a story
- [x] 4.5 Implement `POST /api/stories` creating empty story
- [x] 4.6 Add story_router to `web/api/api_router.py`
- [x] 4.7 Create response schemas in `web/schema/story.py`

## 5. Session Story Integration

- [x] 5.1 Add `story_id` field to SessionCreate schema
- [x] 5.2 Update Session model to store story_id
- [x] 5.3 Modify EngineManager to load story from story_id instead of hard-coded path

## 6. Frontend API Types

- [ ] 6.1 Run `pnpm generate-api-types` to generate TypeScript types

## 7. Frontend Story Components

- [x] 7.1 Create `components/stories/StorySourceBadge.tsx`
- [x] 7.2 Create `components/stories/StoryCard.tsx` with play button
- [x] 7.3 Create `components/stories/StoryList.tsx` page component

## 8. Frontend Routing

- [x] 8.1 Add `/stories` route in `Routes.tsx`
- [x] 8.2 Add Stories link to `Navbar.tsx`

## 9. Cleanup

- [x] 9.1 Move `examples/broken-bulb` to `examples/buzz/broken-bulb`
- [x] 9.2 Remove hard-coded story path from `engine/manager.py`
