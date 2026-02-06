## 1. Add Dependencies

- [ ] 1.1 Add `platformdirs>=4.0.0` to `backend/pyproject.toml`
- [ ] 1.2 Run `uv sync` to install new dependency

## 2. Update Constants Module

- [ ] 2.1 Update `backend/llm_gamebook/constants.py`:
  - [ ] 2.1.1 Import `platformdirs` and `Path`, `Final` types
  - [ ] 2.1.2 Add `USER_DATA_DIR` constant using `platformdirs.user_data_dir()`
  - [ ] 2.1.3 Update any existing references to old database path

## 3. Update Database Creation

- [ ] 3.1 Update `backend/llm_gamebook/db/create_db.py`:
  - [ ] 3.1.1 Import `USER_DATA_DIR` from constants
  - [ ] 3.1.2 Update database path to `USER_DATA_DIR / "llm-gamebook.db"`
  - [ ] 3.1.3 Verify connection URL uses `sqlite+aiosqlite` protocol

## 4. Implement Directory Creation

- [ ] 4.1 Update `backend/llm_gamebook/main.py` lifespan function:
  - [ ] 4.1.1 Create `USER_DATA_DIR` if it does not exist
  - [ ] 4.1.2 Add explicit error handling with clear error message

## 5. Handle Example Project Path

- [ ] 5.1 Update `backend/llm_gamebook/web/get_model.py`:
  - [ ] 5.1.1 Decide on approach (A, B, C, or D from design doc)
  - [ ] 5.1.2 Implement chosen approach for example project path

## 6. Update Tests

- [ ] 6.1 Update `backend/tests/conftest.py`:
  - [ ] 6.1.1 Update `examples_path` fixture to use appropriate path
  - [ ] 6.1.2 Verify tests pass with new directory structure

## 7. Verification

- [ ] 7.1 Run `uv run pytest` - ensure tests pass
- [ ] 7.2 Run `uv run ruff check` - linting
- [ ] 7.3 Run `uv run mypy` - type checking
- [ ] 7.4 Manual test:
  - [ ] 7.4.1 Start backend: `uv run python -m llm_gamebook.main web`
  - [ ] 7.4.2 Verify database created in user data directory
  - [ ] 7.4.3 Create a session
  - [ ] 7.4.4 Verify data persisted
  - [ ] 7.4.5 Restart and verify data still available
