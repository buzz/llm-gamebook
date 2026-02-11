## 1. Project Setup

- [ ] 1.1 Create `backend/tests/integration/` directory structure
- [ ] 1.2 Create `__init__.py` files in test directories

## 2. MockLLMAgent Implementation

- [ ] 2.1 Create `backend/tests/integration/mocks/llm_agent.py`
- [ ] 2.2 Implement `MockLLMAgent.__init__()` with response queue
- [ ] 2.3 Implement `expect_tool_call()` method to queue expected responses
- [ ] 2.4 Implement `get_response()` async method returning tool calls
- [ ] 2.5 Implement system prompt validation methods
- [ ] 2.6 Add error handling for unexpected queries

## 3. MockPlayer Implementation

- [ ] 3.1 Create `backend/tests/integration/mocks/player.py`
- [ ] 3.2 Implement `MockPlayer.__init__()` wrapping existing `story_engine` fixture
- [ ] 3.3 Implement `take_action()` method for submitting player actions
- [ ] 3.4 Implement `assert_current_location()` for state verification
- [ ] 3.5 Implement `assert_content_active()` for conditional content checks

## 4. Share Fixtures with Integration Tests

- [ ] 4.1 Lift `story_engine` fixture from `llm_gamebook/conftest.py` to `tests/conftest.py`
- [ ] 4.2 Create `mock_llm_agent` fixture in `tests/conftest.py`
- [ ] 4.3 Create `mock_player` fixture in `tests/conftest.py`

## 5. Broken Bulb Integration Test

- [ ] 5.1 Create `backend/tests/integration/test_storyengine.py`
- [ ] 5.2 Implement test for initial bedroom state
- [ ] 5.3 Implement test for location transition (bedroom → living_room)
- [ ] 5.4 Implement test for system prompt content validation
- [ ] 5.5 Implement test for conditional leaflet content
- [ ] 5.6 Implement complete story run test combining all scenarios

## 6. Verify and Refine

- [ ] 6.1 Run `pytest tests/integration/test_storyengine.py` to verify tests pass
- [ ] 6.2 Run `uv run ruff check` to ensure no linting issues
- [ ] 6.3 Run `uv run mypy llm_gamebook` for type checking
