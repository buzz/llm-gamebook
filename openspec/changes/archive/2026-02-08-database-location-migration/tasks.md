## 1. Add Dependencies

- [x] 1.1 Add `platformdirs>=4.0.0` to `backend/pyproject.toml`
- [x] 1.2 Run `uv sync` to install new dependency

## 2. Update Constants Module

- [x] 2.1 Update `backend/llm_gamebook/constants.py`:
  - [x] 2.1.1 Import `platformdirs` and `Path`, `Final` types
  - [x] 2.1.2 Add `USER_DATA_DIR` constant using `platformdirs.user_data_dir()`
  - [x] 2.1.3 Update any existing references to old database path

## 3. Update Database Creation

- [x] 3.1 Update `backend/llm_gamebook/db/db_engine.py`:
  - [x] 3.1.1 Import `USER_DATA_DIR` from constants
  - [x] 3.1.2 Update database path to `USER_DATA_DIR / "llm-gamebook.db"`
  - [x] 3.1.3 Verify connection URL uses `sqlite+aiosqlite` protocol

## 4. Implement Directory Creation

- [x] 4.1 Update `backend/llm_gamebook/web/app.py` lifespan function:
  - [x] 4.1.1 Create `USER_DATA_DIR` if it does not exist
  - [x] 4.1.2 Add explicit error handling with clear error message

## 5. Handle Example Project Path

- [x] 5.1 Update `backend/llm_gamebook/web/get_model.py`:
  - [x] 5.1.1 Decide on approach (A, B, C, or D from design doc)
  - [x] 5.1.2 Implement chosen approach for example project path

## 6. Update Tests

- [x] 6.1 Update `backend/tests/conftest.py`:
  - [x] 6.1.1 Update `examples_path` fixture to use appropriate path
  - [x] 6.1.2 Verify tests pass with new directory structure

## 7. Verification

- [x] 7.1 Run `uv run pytest` - ensure tests pass
- [x] 7.2 Run `uv run ruff check` - linting
- [x] 7.3 Run `uv run mypy` - type checking
- [x] 7.4 Manual test:
  - [x] 7.4.1 Start backend: `uv run python -m llm_gamebook.main web`
  - [x] 7.4.2 Verify database created in user data directory
  - [x] 7.4.3 Create a session
  - [x] 7.4.4 Verify data persisted
  - [x] 7.4.5 Restart and verify data still available
