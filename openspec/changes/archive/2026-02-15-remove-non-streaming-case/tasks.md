## 1. Backend Engine Changes

- [x] 1.1 Remove `streaming: bool = False` parameter from `generate_response()` in `engine.py`
- [x] 1.2 Remove the non-streaming `else` branch (lines 81-86) in `engine.py`
- [x] 1.3 Remove the `if streaming:` check - just run streaming code unconditionally

## 2. Test Updates

- [x] 2.1 Update `test_engine.py` - remove `streaming=False` from 7 test calls:
  - `test_story_engine_generate_response_non_streaming`
  - `test_story_engine_generate_response_error_httpx`
  - `test_story_engine_generate_response_error_openai`
  - `test_story_engine_generate_response_error_agent_run`
  - `test_story_engine_generate_response_error_model_api`
  - `test_story_engine_generate_response_error_model_http`
  - `test_set_model_allows_subsequent_requests_with_new_model`
- [x] 2.2 Update `broken_bulb/test_story_flow.py` - remove `streaming=False` from 3 test calls

## 4. MockModel Streaming Migration

- [x] 4.1 Update `MockModel` in `broken_bulb/mocks/model.py` to support streaming via `stream_function`
- [x] 4.2 Remove `@pytest.mark.xfail` from `test_story_flow.py`
- [x] 4.3 Verify test passes: `uv run pytest tests/broken_bulb/test_story_flow.py`

## 3. Verification

- [x] 3.1 Run backend linter: `cd backend && uv run ruff check llm_gamebook`
- [x] 3.2 Run type checker: `cd backend && uv run mypy llm_gamebook` (5 pre-existing TUI errors)
- [x] 3.3 Run tests: `cd backend && uv run pytest`
