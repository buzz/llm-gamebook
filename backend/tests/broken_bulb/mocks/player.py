from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.engine.engine import StoryEngine


class MockPlayer:
    """Mock player for testing StoryEngine integration.

    Wraps a StoryEngine instance to provide an interface for submitting player actions.
    """

    def __init__(self, story_engine: StoryEngine) -> None:
        self._engine = story_engine

    async def send_text(self, content: str, db_session: AsyncDbSession) -> None:
        await self._engine.session_adapter.create_user_request(db_session, content)
