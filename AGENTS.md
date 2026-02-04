# Agent Guidelines

Monorepo with Python backend (`backend/`) and React frontend (`frontend/`).

## Commands

### Python
Run inside `backend/` directory:

- Lint: `uv run ruff check`
- Type check: `uv run mypy llm_gamebook`
- Format: `uv run ruff format llm_gamebook`
- Format (only check): `uv run ruff format --check llm_gamebook`
- Test single: `uv run pytest tests/foo/test_bar.py -v`
- All tests: `uv run pytest`
- Generate `coverage.md`: `uv run pytest --cov --cov-report markdown`
- Install dependencies: `uv sync`
- Add package
  - `uv add PKG` or
  - `uv add --dev PKG` for dev dependency
- Remove package: `uv remove PKG`

### Node.js
Run inside `frontend/` directory:

- Lint: `pnpm lint`
- Format (only check): `pnpm format`
- Format: `pnpm format:check`
- Type check: `pnpm typecheck`
- Tests: `pnpm test`
- Generate API types (`frontend/src/types/openapi.d.ts`): `pnpm generate-api-types`
- Install dependencies: `pnpm install`
- Add package
  - `pnpm add PKG`
  - `pnpm add --save-dev PKG` for dev dependency
- Remove package: `pnpm remove PKG`

## Code Style

### Python
- Imports
  - Use absolute imports
  - Group in sections (stdlib, third-party, local)
  - Use explicit imports (avoid `import *`)
  - Follow isort configuration in ruff_defaults.toml
  - Imports must only appear at the top of a file.
- Formatting
  - 100-char line limit
  - Use ruff formatter for consistent code style
  - PEP 8 standards
- Types
  - Use type hints consistently
  - Use modern Python 3.14+ type hints
  - Prefer `T | None` over `Union[T, None]`
  - Prefer `list` over `List`
  - Avoid adding `from __future__ import annotations` (not needed for modern Python 3.14+)
- Naming: snake_case for functions/variables, PascalCase for classes
- Error Handling
  - Use Python exceptions
  - Avoid silent failures
  - Catch only those specific exceptions that are expected to be raised in the try block; CRITICAL: Avoid catching broad `Exception`
  - Make use of `with contextlib.suppress()`
- Docstrings
  - Follow Google Python style guide for docstrings
  - Document all public functions, classes, and methods
  - Include parameter types and descriptions
  - Include return value descriptions for non-trivial functions
- CRITICAL: Never silence linter issues like: BLE001, PLR0904, PLR0912, PLR0914, PLR0915, C901
- Keep `__init__.py` free of logic; only re-exports and metadata.
- Tests
  - Tests live under `tests/`, mirroring the package tree.
  - Name tests `test_*.py`; never place tests in `__init__.py`.
  - AVOID: Coverage-driven tests without behavior

### TypeScript

- Imports
  - Use explicit imports (avoid `import *`)
  - Organize in sections (stdlib, third-party, local)
  - Always keep imports at the top of a file
  - Default: use ESLint and Prettier configuration
- Formatting
  - Use Prettier for consistent code style
  - Follow TypeScript and JavaScript best practices
  - 2-space indentation
  - Use single quotes for strings
- Types
  - Use TypeScript type hints consistently
  - Use type inference where possible
  - Don't add redundant type annotations
- Naming
  - camelCase for variables and functions
  - PascalCase for classes
  - UPPER_CASE for constants
  - Use descriptive names
- Error Handling
  - Use appropriate error types
  - Avoid silent failures
  - Handle specific errors that are expected
- Testing
  - Use mocking sparingly; default to integration tests if possible
  - React Testing Library: Avoid `data-testid`; use semantic queries first.
