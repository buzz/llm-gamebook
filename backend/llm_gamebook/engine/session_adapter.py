from collections.abc import AsyncIterable
from logging import getLogger
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import ValidationError
from pydantic_ai import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import (
    create_message,
    get_latest_message_with_state,
    get_message_count,
    get_messages,
)
from llm_gamebook.db.crud.session import delete_session, get_session
from llm_gamebook.db.models import Message, Session
from llm_gamebook.db.models.part import Part
from llm_gamebook.engine.message import ResponseUserRequestMessage, SessionDeleted
from llm_gamebook.story.state import SessionStateData

logger = getLogger(__name__)

if TYPE_CHECKING:
    from llm_gamebook.message_bus import MessageBus
    from llm_gamebook.story import StoryContext
    from llm_gamebook.web.schemas.session.message import ModelRequestCreate


class SessionAdapter:
    """SQL-backed message history."""

    def __init__(self, session_id: UUID, context: "StoryContext", bus: "MessageBus") -> None:
        self._session_id = session_id
        self._context = context
        self._bus = bus

    async def get_session(self, db_session: AsyncDbSession) -> Session | None:
        return await get_session(db_session, self._session_id)

    async def delete_session(self, db_session: AsyncDbSession) -> None:
        await delete_session(db_session, self._session_id)
        self._bus.publish(SessionDeleted(self._session_id))

    async def get_message_count(self, db_session: AsyncDbSession) -> int:
        return await get_message_count(db_session, self._session_id)

    async def get_message_history(self, db_session: AsyncDbSession) -> AsyncIterable[ModelMessage]:
        # Message history
        messages = await get_messages(db_session, self._session_id)

        if not messages:
            # Introduction message (only on empty chat)
            req = ModelRequest([UserPromptPart(content=await self._context.get_intro_message())])
            message = Message.from_model_request(self._session_id, req)
            await create_message(db_session, message)
            yield req
        else:
            model_messages = (msg.to_model_message() for msg in messages)
            for msg in model_messages:
                # Keep only relevant parts
                if isinstance(msg, ModelResponse):
                    msg.parts = [p for p in msg.parts if isinstance(p, TextPart)]
                else:  # ModelRequest
                    msg.parts = [p for p in msg.parts if isinstance(p, UserPromptPart)]

                # Skip empty messages
                if len(msg.parts) == 0:
                    continue

                yield msg

    async def load_state(self, db_session: AsyncDbSession) -> SessionStateData | None:
        message = await get_latest_message_with_state(db_session, self._session_id)
        if message is None or message.state is None:
            return None

        try:
            return SessionStateData.model_validate(message.state)
        except (ValidationError, TypeError, ValueError) as err:
            logger.warning(
                "Corrupted state JSON in message %s for session %s: %s",
                message.id,
                self._session_id,
                err,
            )
            return None

    async def create_user_request(
        self, db_session: AsyncDbSession, message_in: "ModelRequestCreate"
    ) -> Message:
        message = Message(
            **message_in.model_dump(exclude={"parts"}),
            session_id=self._session_id,
            parts=[Part(**p.model_dump()) for p in message_in.parts],
        )
        message = await create_message(db_session, message)
        self._bus.publish(ResponseUserRequestMessage(self._session_id))
        return message

    @property
    def session_id(self) -> UUID:
        return self._session_id
