# E2E tests

Playwright (Python) end-to-end tests for LLM Gamebook. Tests run against a
real backend and frontend, so they exercise the full stack including the
Vite dev-server `/api` proxy.

## Setup (one-time)

```bash
cd e2e
uv sync
uv run playwright install chromium
```

## Run

```bash
cd e2e
uv run pytest
```

Useful variations:

- Headed (visible) browser: `uv run pytest --headed`
- Single test: `uv run pytest test_smoke.py -v`
- Another browser: `uv run pytest --browser firefox`
- Trace on failure: `uv run pytest --trace on` (view with `uv run playwright show-trace`)

## How it works

The session fixture `base_url` in `conftest.py` starts the backend
(`uv run python -m llm_gamebook.main web --port <free>`) and the frontend
(`pnpm dev --host 127.0.0.1 --port <free> --strictPort`) on free localhost
ports (pytest-asyncio's `unused_tcp_port_factory`) and stops them when the
session ends. The frontend proxies `/api` to the backend port via the
`API_PROXY_TARGET` environment variable (see `frontend/vite.config.ts`).
Free ports mean e2e runs never collide with dev servers on the default
ports, and can run in parallel with them.

Server logs are written to `e2e/.logs/` (and dumped on startup failure).

## Notes

- The e2e suite lives in its own uv project (separate `pyproject.toml` and
  venv) so `pytest backend/` never picks these tests up and Playwright stays
  out of the backend dependencies.
- No LLM API keys are required by the smoke test; only tests that drive an
  actual LLM session need a configured model.
