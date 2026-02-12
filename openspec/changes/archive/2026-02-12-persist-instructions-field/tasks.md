# Implementation Tasks

## Database

- [x] Add `instructions` column to `Message` model in `backend/llm_gamebook/db/models/message.py`

## API

- [x] Add `instructions` field to message response schemas in `backend/llm_gamebook/schemas/message.py`
- [x] Run database migration (Alembic) to create the column

## Frontend

- [x] Regenerate API types: `cd frontend && pnpm generate-api-types`

## Verification

- [x] Run linter: `cd backend && uv run ruff check`
- [x] Run type check: `cd backend && uv run mypy llm_gamebook`
- [x] Run tests: `cd backend && uv run pytest`
