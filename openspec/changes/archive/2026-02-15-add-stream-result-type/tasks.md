## 1. Implement StreamResult Type

- [x] 1.1 Add `StreamResult` dataclass to `backend/llm_gamebook/engine/_runner.py`
- [x] 1.2 Add docstrings to each field explaining its purpose and contents

## 2. Update Callers

- [x] 2.1 Update `StreamRunner.run()` return type annotation to use `StreamResult`
- [x] 2.2 Update `StoryEngine.generate_response()` to use named fields from `StreamResult`

## 3. Verify

- [x] 3.1 Run lint: `uv run ruff check llm_gamebook/engine/`
- [x] 3.2 Run type check: `uv run mypy llm_gamebook/engine/`
- [x] 3.3 Run tests: `uv run pytest tests/llm_gamebook/engine/`
