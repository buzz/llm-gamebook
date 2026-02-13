# Agent Guidelines

Monorepo with Python backend (`backend/`) and React frontend (`frontend/`).

## Project Structure

```
llm-gamebook/
├── backend/           # Python FastAPI backend
│   ├── llm_gamebook/  # Main package
│   └── tests/         # Python tests (mirrors package structure)
└── frontend/          # React + TypeScript frontend
    └── src/           # Frontend source code
```

## Commands

### Python
Run inside `backend/` directory:

- Lint: `uv run ruff check`
- Type check: `uv run mypy llm_gamebook`
- Format: `uv run ruff format llm_gamebook`
- Format (only check): `uv run ruff format --check llm_gamebook`
- Test single: `uv run pytest tests/path/to/test_file.py::test_name -v`
- Test single file: `uv run pytest tests/foo/test_bar.py -v`
- All tests: `uv run pytest`
- Test with coverage: `uv run pytest --cov --cov-report markdown`
- Install dependencies: `uv sync`
- Add package: `uv add PKG` or `uv add --dev PKG` (dev dependency)
- Remove package: `uv remove PKG`

### Node.js
Run inside `frontend/` directory:

- Dev server: `pnpm dev`
- Build: `pnpm build`
- Lint: `pnpm lint`
- Lint with fix: `pnpm lint:fix`
- Format: `pnpm format`
- Format (only check): `pnpm format:check`
- Type check: `pnpm typecheck`
- Tests: `pnpm test`
- Generate API types: `pnpm generate-api-types` (requires backend running at localhost:8000)
- Install dependencies: `pnpm install`
- Add package: `pnpm add PKG` or `pnpm add --save-dev PKG` (dev dependency)
- Remove package: `pnpm remove PKG`

## Code Style

### Python

- **Imports**: Use absolute imports, group in sections (stdlib, third-party, local), use explicit imports (`import *` forbidden), follow isort configuration in ruff_defaults.toml, imports must only appear at the top of a file.
- **Formatting**: 100-char line limit, use ruff formatter, follow PEP 8 standards.
- **Types**: Use type hints consistently, use modern Python 3.14+ type hints, prefer `T | None` over `Union[T, None]`, prefer `list` over `List`, avoid adding `from __future__ import annotations`.
- **Naming**: snake_case for functions/variables, PascalCase for classes.
- **Error Handling**: Use Python exceptions, avoid silent failures, catch only specific exceptions expected to be raised, use `with contextlib.suppress()` for suppressible exceptions. CRITICAL: Never catch broad `Exception`.
- **Docstrings**: Follow Google Python style guide, document all public functions/classes/methods, include parameter types/descriptions and return value descriptions for non-trivial functions.
- **Linting**: Never silence linter issues like BLE001, PLR0904, PLR0912, PLR0914, PLR0915, C901.
- **`__init__.py`**: Keep free of logic; only re-exports and metadata.
- **Tests**: Tests live under `tests/`, mirroring the package tree, name tests `test_*.py`, avoid coverage-driven tests without behavior.

### TypeScript

- **Imports**: Use explicit imports (`import *` forbidden), organize in sections (stdlib, third-party, local), keep imports at the top of files, use ESLint/Prettier configuration.
- **Formatting**: Prettier for code style, 2-space indentation, single quotes for strings.
- **Types**: Use type hints consistently, use type inference where possible, don't add redundant type annotations.
- **Naming**: camelCase for variables/functions, PascalCase for classes, UPPER_CASE for constants, use descriptive names.
- **Error Handling**: Use appropriate error types, avoid silent failures, handle only specific expected errors.
- **Testing**: Use mocking sparingly, prefer integration tests, React Testing Library: avoid `data-testid`, use semantic queries first.
- **State Management**: Uses Redux Toolkit for global state, React hooks for local state.
- **Routing**: Uses `wouter` for routing (lightweight React router).
- **UI Framework**: Mantine v8 components.

## Important Configuration Details

### Python (pyproject.toml)
- Requires Python 3.13+
- Uses strict mypy (`disallow_any_explicit = true`)
- Pydantic mypy plugin enabled with strict settings
- Ruff linter with extensive rules enabled (see pyproject.toml for full list)
- pytest-asyncio for async tests with `asyncio_mode = "auto"`

### Frontend (package.json)
- Uses Vite for build tooling
- TypeScript with strict mode
- ESLint with react-x, react-hooks, and import plugins
- Vitest for testing

## Best Practices

1. **Before committing**: Run lint, typecheck, and tests for both backend and frontend.
2. **API types**: Regenerate after backend API changes using `pnpm generate-api-types`.
3. **Database**: Uses SQLModel with SQLite (aiosqlite) for async database operations.
4. **LLM Integration**: Uses Pydantic AI for LLM interactions with support for multiple providers.
5. **TUI**: Backend includes a Textual-based terminal UI (`textual` package).
