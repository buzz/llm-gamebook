## 1. Backend Constants

- [ ] 1.1 Add `STORIES_DIR` and `EXAMPLES_DIR` to `constants.py`
- [ ] 1.2 Update `app.py` lifespan to create `STORIES_DIR` on startup

## 2. Story Discovery

- [ ] 2.1 Create `backend/llm_gamebook/story_project/__init__.py`
- [ ] 2.2 Create `story_project/schemas.py` with StorySource enum and Story response model
- [ ] 2.3 Create `story_project/discovery.py` with `discover_stories()` function
- [ ] 2.4 Implement discovery scanning for `examples/{namespace}/{story}/` directories
- [ ] 2.5 Implement discovery scanning for `STORIES_DIR/{namespace}/{story}/` directories
- [ ] 2.6 Derive story name from path: `{namespace}/{story}`

## 3. Story Manager

- [ ] 3.1 Create `story_project/manager.py` with StoryManager class
- [ ] 3.2 Implement `list_stories()` combining examples and user stories
- [ ] 3.3 Implement `get_story(story_id)` for individual story lookup
- [ ] 3.4 Implement `create_story(name, title)` creating directory + `llm-gamebook.yaml`

## 4. Story API Router

- [ ] 4.1 Create `web/api/story_router.py` with `/api/stories` endpoints
- [ ] 4.2 Implement `GET /api/stories` with optional source filter
- [ ] 4.3 Implement `GET /api/stories/{id}` returning story details
- [ ] 4.4 Implement `DELETE /api/stories/{id}` deleting a story
- [ ] 4.5 Implement `POST /api/stories` creating empty story
- [ ] 4.6 Add story_router to `web/api/api_router.py`
- [ ] 4.7 Create response schemas in `web/schema/story.py`

## 5. Session Story Integration

- [ ] 5.1 Add `story_id` field to SessionCreate schema
- [ ] 5.2 Update Session model to store story_id
- [ ] 5.3 Modify EngineManager to load story from story_id instead of hard-coded path

## 6. Frontend API Types

- [ ] 6.1 Run `pnpm generate-api-types` to generate TypeScript types

## 7. Frontend Story Components

- [ ] 7.1 Create `components/stories/StorySourceBadge.tsx`
- [ ] 7.2 Create `components/stories/StoryCard.tsx` with play button
- [ ] 7.3 Create `components/stories/StoryList.tsx` page component

## 8. Frontend Routing

- [ ] 8.1 Add `/stories` route in `Routes.tsx`
- [ ] 8.2 Add Stories link to `Navbar.tsx`

## 9. Cleanup

- [ ] 9.1 Move `examples/broken-bulb` to `examples/buzz/broken-bulb`
- [ ] 9.2 Remove hard-coded story path from `engine/manager.py`
