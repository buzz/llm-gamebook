# Implementation Tasks

## Database

- [ ] Add `instructions` column to `Message` model in `backend/llm_gamebook/db/models/message.py`

## API

- [ ] Add `instructions` field to message response schemas in `backend/llm_gamebook/schemas/message.py`
- [ ] Run database migration (Alembic) to create the column

## Frontend

- [ ] Regenerate API types: `cd frontend && pnpm generate-api-types`

## Verification

- [ ] Run linter: `cd backend && uv run ruff check`
- [ ] Run type check: `cd backend && uv run mypy llm_gamebook`
- [ ] Run tests: `cd backend && uv run pytest`
