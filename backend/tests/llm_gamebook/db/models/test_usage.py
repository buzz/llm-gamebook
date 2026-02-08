from pydantic_ai.usage import RequestUsage
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Message, Usage


def test_usage_from_request_usage() -> None:
    request_usage = RequestUsage(
        input_tokens=100,
        output_tokens=200,
        cache_read_tokens=50,
        cache_write_tokens=25,
    )

    usage = Usage.from_request_usage(request_usage)

    assert usage.input_tokens == 100
    assert usage.output_tokens == 200
    assert usage.cache_read_tokens == 50
    assert usage.cache_write_tokens == 25


async def test_usage_fields(db_session: AsyncDbSession, message: Message) -> None:
    usage = Usage(
        input_tokens=150,
        output_tokens=300,
        cache_read_tokens=75,
        cache_write_tokens=40,
        message_id=message.id,
    )
    db_session.add(usage)
    await db_session.commit()
    await db_session.refresh(usage)

    assert usage.id is not None
    assert usage.input_tokens == 150
    assert usage.output_tokens == 300
    assert usage.cache_read_tokens == 75
    assert usage.cache_write_tokens == 40
    assert usage.message_id == message.id
