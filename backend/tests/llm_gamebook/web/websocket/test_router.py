import pytest


@pytest.mark.skip
async def test_websocket_endpoint_connection(
    websocket, db_session, story_engine_manager, message_bus
) -> None:
    pass


@pytest.mark.skip
async def test_websocket_endpoint_handles_messages(
    websocket, db_session, story_engine_manager, message_bus
) -> None:
    pass
