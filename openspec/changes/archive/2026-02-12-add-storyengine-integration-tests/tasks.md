## 1. Project Setup

- [x] 1.1 Create `backend/tests/integration/` directory structure
- [x] 1.2 Create `__init__.py` files in test directories

## 2. MockLLMAgent Implementation

- [x] 2.1 Create `backend/tests/integration/mocks/llm_agent.py`
- [x] 2.2 Implement `MockLLMAgent.__init__()` with response queue
- [x] 2.3 Implement `expect_tool_call()` method to queue expected responses
- [x] 2.4 Implement `get_response()` async method returning tool calls
- [x] 2.5 Implement system prompt validation methods
- [x] 2.6 Add error handling for unexpected queries
- [ ] 2.2 Implement `MockLLMAgent.__init__()` with response queue
- [ ] 2.3 Implement `expect_tool_call()` method to queue expected responses
- [ ] 2.4 Implement `get_response()` async method returning tool calls
- [ ] 2.5 Implement system prompt validation methods
- [ ] 2.6 Add error handling for unexpected queries

## 3. MockPlayer Implementation

- [x] 3.1 Create `backend/tests/integration/mocks/player.py`
- [x] 3.2 Implement `MockPlayer.__init__()` wrapping existing `story_engine` fixture
- [x] 3.3 Implement `take_action()` method for submitting player actions
- [x] 3.4 Implement `assert_current_location()` for state verification
- [x] 3.5 Implement `assert_content_active()` for conditional content checks
- [ ] 3.2 Implement `MockPlayer.__init__()` wrapping existing `story_engine` fixture
- [ ] 3.3 Implement `take_action()` method for submitting player actions
- [ ] 3.4 Implement `assert_current_location()` for state verification
- [ ] 3.5 Implement `assert_content_active()` for conditional content checks

## 4. Share Fixtures with Integration Tests

- [x] 4.1 Lift `story_engine` fixture from `llm_gamebook/conftest.py` to `tests/conftest.py`
- [x] 4.2 Create `mock_llm_agent` fixture in `tests/conftest.py`
- [x] 4.3 Create `mock_player` fixture in `tests/conftest.py`

## 5. Broken Bulb Integration Test

- [x] 5.1 Create `backend/tests/integration/test_storyengine.py`
- [x] 5.2 Implement test for initial bedroom state
- [x] 5.3 Implement test for location transition (bedroom → living_room)
- [ ] 5.4 Implement test for system prompt content validation
- [ ] 5.5 Implement test for conditional leaflet content
- [ ] 5.6 Implement complete story run test combining all scenarios

## 6. Verify and Refine

- [ ] 6.1 Run `pytest tests/integration/test_storyengine.py` to verify tests pass
- [ ] 6.2 Run `uv run ruff check` to ensure no linting issues
- [ ] 6.3 Run `uv run mypy llm_gamebook` for type checking
