import pytest

from llm_gamebook.db.models.session import Session


@pytest.mark.skip
async def test_story_engine_generate_response_streaming(
    session: Session, model, state, bus, db_session
) -> None:
    pass


@pytest.mark.skip
async def test_story_engine_generate_response_non_streaming(
    session: Session, model, state, bus, db_session
) -> None:
    pass


@pytest.mark.skip
async def test_story_engine_generate_response_http_error(
    session: Session, model, state, bus, db_session
) -> None:
    pass


@pytest.mark.skip
async def test_story_engine_generate_response_openai_error(
    session: Session, model, state, bus, db_session
) -> None:
    pass


@pytest.mark.skip
async def test_prepare_tools_with_messages(session: Session, model, state, bus, ctx, tools) -> None:
    pass


@pytest.mark.skip
async def test_prepare_tools_no_messages(session: Session, model, state, bus, ctx, tools) -> None:
    pass


@pytest.mark.skip
def test_stream_runner_run(session: Session, agent, bus, msg_history, state) -> None:
    pass


@pytest.mark.skip
async def test_stream_runner_handle_model_request_node(
    session: Session, agent, bus, node, run
) -> None:
    pass


@pytest.mark.skip
async def test_stream_runner_handle_call_tools_node(
    session: Session, agent, bus, node, run
) -> None:
    pass


@pytest.mark.skip
async def test_stream_runner_handle_part_start_event(
    session: Session, agent, bus, response, event
) -> None:
    pass


@pytest.mark.skip
async def test_stream_runner_handle_part_delta_event(
    session: Session, agent, bus, response, event
) -> None:
    pass


@pytest.mark.skip
async def test_stream_runner_send_stream_update_debounced(
    session: Session, agent, bus, response
) -> None:
    pass
