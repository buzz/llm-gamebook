from collections.abc import Callable

from fastapi.testclient import TestClient

from llm_gamebook.db.models import Session
from llm_gamebook.web.schema.websocket.message import WebSocketPingMessage


async def test_websocket_endpoint_connection(
    client: TestClient,
    session: Session,
    unused_tcp_port_factory: Callable[[], int],
) -> None:
    port = unused_tcp_port_factory()
    url = f"ws://testclient:{port}/ws"

    with client.websocket_connect(url) as websocket:
        websocket.send_text(WebSocketPingMessage(kind="ping").model_dump_json())
        received = websocket.receive_json()
        assert received.get("kind") == "pong"


async def test_websocket_endpoint_handles_messages(
    client: TestClient,
    session: Session,
    unused_tcp_port_factory: Callable[[], int],
) -> None:
    port = unused_tcp_port_factory()
    url = f"ws://testclient:{port}/ws"

    with client.websocket_connect(url) as websocket:
        websocket.send_text(WebSocketPingMessage(kind="ping").model_dump_json())
        response = websocket.receive_json()
        assert response["kind"] == "pong"

        websocket.send_text('{"kind": "invalid"}')
