from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from llm_gamebook.engine import EngineManager
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.web.app import create_app
from llm_gamebook.web.schema.websocket.openapi import add_websocket_schema


@pytest.fixture
def client(
    db_engine: AsyncEngine,
    message_bus: MessageBus,
    engine_manager: EngineManager,
    unused_tcp_port_factory: Callable[[], int],
) -> Iterator[TestClient]:
    @asynccontextmanager
    async def _test_lifespan(app: FastAPI) -> AsyncIterator[None]:
        add_websocket_schema(app.openapi())
        app.state.db_engine = db_engine
        app.state.bus = message_bus
        app.state.engine_mgr = engine_manager
        yield

    app = create_app(lifespan=_test_lifespan)

    with TestClient(app, client=("testclient", unused_tcp_port_factory())) as client:
        yield client
