## 1. Backend Engine Changes

- [ ] 1.1 Remove `streaming: bool = False` parameter from `generate_response()` in `engine.py`
- [ ] 1.2 Remove the non-streaming `else` branch (lines 81-86) in `engine.py`
- [ ] 1.3 Remove the `if streaming:` check - just run streaming code unconditionally

## 2. Test Updates

- [ ] 2.1 Update `test_engine.py` - remove `streaming=False` from 7 test calls:
  - `test_story_engine_generate_response_non_streaming`
  - `test_story_engine_generate_response_error_httpx`
  - `test_story_engine_generate_response_error_openai`
  - `test_story_engine_generate_response_error_agent_run`
  - `test_story_engine_generate_response_error_model_api`
  - `test_story_engine_generate_response_error_model_http`
  - `test_set_model_allows_subsequent_requests_with_new_model`
- [ ] 2.2 Update `broken_bulb/test_story_flow.py` - remove `streaming=False` from 3 test calls

## 3. Verification

- [ ] 3.1 Run backend linter: `cd backend && uv run ruff check llm_gamebook`
- [ ] 3.2 Run type checker: `cd backend && uv run mypy llm_gamebook`
- [ ] 3.3 Run tests: `cd backend && uv run pytest`
