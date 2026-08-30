"""Shared fixtures for the e2e test suite.

Starts the backend and frontend dev servers on free localhost ports (via
pytest-asyncio's ``unused_tcp_port_factory``) and exposes the frontend URL
as Playwright's ``base_url``. Servers are stopped when the session ends.
"""

import contextlib
import http.client
import os
import signal
import subprocess
import time
import urllib.parse
from collections.abc import Callable, Generator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = Path(__file__).resolve().parent / ".logs"

BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

HOST = "127.0.0.1"

STARTUP_TIMEOUT_S = 120.0
POLL_INTERVAL_S = 0.5


def _is_healthy(url: str) -> bool:
    """Return whether ``url`` responds with a non-client-error status."""
    parsed = urllib.parse.urlparse(url)
    connection = http.client.HTTPConnection(parsed.hostname or "", parsed.port or 80, timeout=2)
    try:
        connection.request("GET", parsed.path or "/")
        response = connection.getresponse()
    except OSError:
        return False
    finally:
        connection.close()
    return response.status < 400


def _tail(path: Path, lines: int = 30) -> str:
    """Return the last ``lines`` of ``path`` (or a placeholder if missing)."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return "<log file not found>"
    return "\n".join(content.splitlines()[-lines:])


def _wait_until_healthy(
    name: str, process: subprocess.Popen[bytes], url: str, log_path: Path
) -> None:
    """Poll ``url`` until it responds, failing early if ``process`` dies."""
    deadline = time.monotonic() + STARTUP_TIMEOUT_S
    while not _is_healthy(url):
        exit_code = process.poll()
        if exit_code is not None:
            message = (
                f"{name} exited with code {exit_code} before becoming ready at "
                f"{url}. Last log lines:\n{_tail(log_path)}"
            )
            raise RuntimeError(message) from None
        if time.monotonic() >= deadline:
            message = (
                f"{name} did not become ready at {url} within "
                f"{STARTUP_TIMEOUT_S:.0f}s. Last log lines:\n{_tail(log_path)}"
            )
            raise TimeoutError(message) from None
        time.sleep(POLL_INTERVAL_S)


def _child_env(extra_env: dict[str, str] | None = None) -> dict[str, str]:
    """Environment for child servers, without our own uv/venv overrides."""
    env = dict(os.environ)
    for key in ("VIRTUAL_ENV", "UV_PROJECT", "UV"):
        env.pop(key, None)
    if extra_env:
        env.update(extra_env)
    return env


def _stop_server(process: subprocess.Popen[bytes]) -> None:
    """Terminate the process group, escalating to SIGKILL if it lingers."""
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(process.pid, signal.SIGKILL)


def _start(
    name: str,
    command: list[str],
    cwd: Path,
    health_url: str,
    extra_env: dict[str, str] | None = None,
) -> subprocess.Popen[bytes]:
    """Start a service and wait until its health URL responds."""
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"{name}.log"
    print(f"[e2e] {name}: starting {' '.join(command)} (log: {log_path})")
    with open(log_path, "wb") as log_file:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            env=_child_env(extra_env),
            start_new_session=True,
        )
    try:
        _wait_until_healthy(name, process, health_url, log_path)
    except (OSError, RuntimeError, TimeoutError):
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise
    return process


@pytest.fixture(scope="session")
def base_url(
    unused_tcp_port_factory: Callable[[], int], tmp_path_factory: pytest.TempPathFactory
) -> Generator[str]:
    """Base URL of the frontend, with backend and frontend guaranteed up.

    Starts the backend (``uv run python -m llm_gamebook.main web``) and the
    frontend (``pnpm dev``, proxying ``/api`` to the backend) on free
    localhost ports, and stops both when the session ends.

    The backend's user data directory (SQLite DB and settings) is redirected
    to a fresh temporary directory via ``XDG_DATA_HOME``, so tests never read
    or write the real user data.
    """
    backend_port = unused_tcp_port_factory()
    frontend_port = unused_tcp_port_factory()
    backend_data_dir = tmp_path_factory.mktemp("backend-data")
    servers = [
        _start(
            "backend",
            ["uv", "run", "python", "-m", "llm_gamebook.main", "web", "--port", str(backend_port)],
            BACKEND_DIR,
            f"http://{HOST}:{backend_port}/openapi.json",
            {"XDG_DATA_HOME": str(backend_data_dir)},
        ),
        _start(
            "frontend",
            ["pnpm", "dev", "--host", HOST, "--port", str(frontend_port), "--strictPort"],
            FRONTEND_DIR,
            f"http://{HOST}:{frontend_port}",
            {"API_PROXY_TARGET": f"http://{HOST}:{backend_port}"},
        ),
    ]
    try:
        yield f"http://{HOST}:{frontend_port}"
    finally:
        for process in servers:
            _stop_server(process)
