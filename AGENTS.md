# Agent Guidelines

Monorepo with Python backend (`backend/`) and React frontend (`frontend/`).

## Project Structure

```
llm-gamebook/
├── backend/           # Python FastAPI backend
│   ├── llm_gamebook/  # Main package
│   └── tests/         # Python tests (mirrors package structure)
├── frontend/          # React + TypeScript frontend
│   └── src/           # Frontend source code
└── e2e/               # Playwright (Python) end-to-end tests (own uv project)
```

## Commands

### Python
Run from `backend/` with `uv run` — tools are version-pinned there, and mypy/ruff/pytest config is discovered relative to the working directory:
- Lint: `uv run ruff check .`
- Type check: `uv run mypy llm_gamebook tests`
- Format: `uv run ruff format .`
- Format (only check): `uv run ruff format --check .`
- Test single: `uv run pytest tests/path/to/test_file.py::test_name -v`
- Test single file: `uv run pytest tests/foo/test_bar.py -v`
- All tests: `uv run pytest`
- Test with coverage: `uv run --with pytest-cov pytest --cov --cov-report markdown`

### Node.js
Run from `frontend/`:
- Build: `pnpm build`
- Lint: `pnpm lint`
- Lint with fix: `pnpm lint:fix`
- Format: `pnpm format`
- Format (only check): `pnpm format:check`
- Type check: `pnpm typecheck`
- Tests: `pnpm test`
- Generate API types: `pnpm generate-api-types` (requires backend running at localhost:8000)

### E2E (Playwright, Python)
- Setup (one-time): `cd e2e && uv sync && uv run playwright install chromium`
- Run: `cd e2e && uv run pytest` (servers auto-start on free ports; headed: `--headed`)

## Testing (Testing Trophy)

Goal: maximum confidence that the app works for its users per unit of time. **Write tests. Not too many. Mostly integration.**

Trophy, bottom → top: **static → unit → integration → e2e**. Going up, tests get slower and more expensive but give more confidence ("the more your tests resemble the way your software is used, the more confidence they can give you"). Spend most effort at the integration level.

| Level | Verifies | Mocking | Use for |
| --- | --- | --- | --- |
| Static (mypy, tsc, ruff, eslint) | Typos, type errors | — | Let it do this job; never write tests for what types/lint already catch |
| Unit | Single function/class | Max (deps mocked) | Pure business-logic edge cases (pricing, parsing, state transitions) |
| Integration | Several units working together | Minimal | **Default choice**; flows across component→state→API or service→db |
| E2E | Full app, driven like a user | ~none | One happy path per top-priority feature |

Rules:

- **Cheapest level that proves the use case.** Type error → static; logic edge case → unit; units cooperating → integration; full user journey → e2e. If a level can't prove it (e.g., unit tests can't prove a dependency is called correctly), go up.
- **Test use cases, not code.** Test title = user-observable behavior ("returns an empty array for a falsy value"), never a branch/line. Code coverage ≠ use case coverage; don't chase 100%, don't test logic-free code.
- **No implementation details.** Exercise only what the code's users can see: inputs in, observable outputs/side effects out (React: props in, rendered DOM + user interactions; API: request in, response out). Never assert on internal state, private helpers, or internal components. Such tests fail on behavior-preserving refactors (false negatives) and pass while behavior is broken (false positives).
- **Mock less.** Every mock deletes confidence in the integration between the tested unit and the mock. Mock only outer boundaries (HTTP via MSW, email, payments) or nondeterminism (time, random). Backend: use a real test DB with fixtures; don't mock repository/DB layers.
- **Refactor-proof:** you should almost never need to change a test during a behavior-preserving refactor.
- **What to test first:** "What would be the worst thing to break in this app?" → E2E happy path for that feature, then integration tests for its edge cases, then unit tests for the complex logic behind them.

Recipe: pick a risky area → narrow to one unit/use case → name its users (caller, API client, end user) → write the manual steps a user would take to verify it → automate exactly those steps.

## Git & Worktree Workflow

**This is the default workflow for any change to the codebase, unless the user explicitly states otherwise.** Parallel sessions may be active in the main source tree at the same time, so never work directly in the main worktree.

1. **Create a worktree in the parent directory.** From the main worktree, for work on `<topic>` (e.g. an OpenSpec change name):
   ```bash
   git worktree add ../<topic> -b feat/<topic>
   ```
   This creates `<parent>/<topic>` on a new `feat/<topic>` branch, following the naming of existing worktrees (e.g. `../session-state-stage-5` → `feat/session-state-stage-5`).
2. **Work inside the worktree and commit there.** All edits, tests, and commits happen in the worktree (conventional commits). The Python venv (`backend/.venv`) is gitignored — if the worktree is based on the same commit (or compatible dependencies), symlink it from the main worktree instead of reinstalling:
   ```bash
   ln -sfn <main-worktree>/backend/.venv <worktree>/backend/.venv
   ```
   Otherwise create a fresh environment with `uv`.
3. **Merge back into the main worktree only after explicit user confirmation.** Present the diff/summary of the work and wait for the user to review and explicitly confirm. Then rebase the branch onto `main` and fast-forward, so no merge commit is created:
   ```bash
   # In the feature worktree, rebase onto main (resolve any conflicts here):
   git rebase main
   # In the main worktree:
   git merge --ff-only feat/<topic>
   ```
   Verify the merge with lint, typecheck, and tests in the main worktree. Never merge without the user's explicit go-ahead.
4. **Remove the worktree and branch.** Once the merge is done (and after the user confirms cleanup if in doubt):
   ```bash
   git worktree remove ../<topic>
   git branch -d feat/<topic>
   ```

## Code Style

### Python
- **Imports**: Use absolute imports, group in sections (stdlib, third-party, local), use explicit imports (`import *` forbidden), follow the isort configuration in `backend/pyproject.toml`, imports must only appear at the top of a file.
- **Formatting**: 100-char line limit, use ruff formatter, follow PEP 8 standards.
- **Types**: Use type hints consistently, use modern Python 3.14+ type hints, prefer `T | None` over `Union[T, None]`, prefer `list` over `List`, avoid adding `from __future__ import annotations`.
- **Naming**: snake_case for functions/variables, PascalCase for classes.
- **Error Handling**: Use Python exceptions, avoid silent failures, catch only specific exceptions expected to be raised, use `with contextlib.suppress()` for suppressible exceptions. CRITICAL: Never catch broad `Exception`.
- **Docstrings**: Follow Google Python style guide, document all public functions/classes/methods, include parameter types/descriptions and return value descriptions for non-trivial functions.
- **Linting**: Never silence linter issues like BLE001, PLR0904, PLR0912, PLR0914, PLR0915, C901.
- **`__init__.py`**: Keep free of logic; only re-exports and metadata.
- **Tests**: Tests live under `backend/tests/`, mirroring the package tree, name tests `test_*.py`, avoid coverage-driven tests without behavior.

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

### Python (backend/pyproject.toml)
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
