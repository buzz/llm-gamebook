## 1. Implement StreamResult Type

- [ ] 1.1 Add `StreamResult` dataclass to `backend/llm_gamebook/engine/_runner.py`
- [ ] 1.2 Add docstrings to each field explaining its purpose and contents

## 2. Update Callers

- [ ] 2.1 Update `StreamRunner.run()` return type annotation to use `StreamResult`
- [ ] 2.2 Update `StoryEngine.generate_response()` to use named fields from `StreamResult`

## 3. Verify

- [ ] 3.1 Run lint: `uv run ruff check llm_gamebook/engine/`
- [ ] 3.2 Run type check: `uv run mypy llm_gamebook/engine/`
- [ ] 3.3 Run tests: `uv run pytest tests/llm_gamebook/engine/`
