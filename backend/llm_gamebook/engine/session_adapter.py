from collections.abc import AsyncIterable, Iterable, Sequence
from contextlib import suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic_ai import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import (
    create_message,
    create_messages,
    get_message_count,
    get_messages,
)
from llm_gamebook.db.crud.session import delete_session, get_session
from llm_gamebook.db.models import Message, Session
from llm_gamebook.db.models.part import Part

if TYPE_CHECKING:
    from llm_gamebook.message_bus import MessageBus
    from llm_gamebook.story.state import StoryState
    from llm_gamebook.web.schema.session.message import ModelRequestCreate


class SessionAdapter:
    """SQL-backed message history."""

    def __init__(self, session_id: UUID, state: "StoryState", bus: "MessageBus") -> None:
        self._session_id = session_id
        self._state = state
        self._bus = bus

    async def get_session(self, db_session: AsyncDbSession) -> Session | None:
        return await get_session(db_session, self._session_id)

    async def delete_session(self, db_session: AsyncDbSession) -> None:
        await delete_session(db_session, self._session_id)
        self._bus.publish("engine.session.deleted", self._session_id)

    async def get_message_count(self, db_session: AsyncDbSession) -> int:
        return await get_message_count(db_session, self._session_id)

    async def get_message_history(self, db_session: AsyncDbSession) -> AsyncIterable[ModelMessage]:
        yield await self._generate_initial_request()
        messages = await get_messages(db_session, self._session_id)
        as_dicts = [msg.to_dict() for msg in messages]
        model_messages = ModelMessagesTypeAdapter.validate_python(as_dicts)
        for msg in model_messages:
            # Skip system prompt/first request as we generate it dynamically
            if isinstance(msg, ModelRequest) and any(
                isinstance(p, SystemPromptPart) for p in msg.parts
            ):
                continue

            # Keep only relevant parts
            if isinstance(msg, ModelResponse):
                msg.parts = [p for p in msg.parts if isinstance(p, TextPart)]
            else:  # ModelRequest
                msg.parts = [p for p in msg.parts if isinstance(p, UserPromptPart)]

            # Skip empty messages
            if len(msg.parts) == 0:
                continue

            yield msg

    async def _generate_initial_request(self) -> ModelRequest:
        return ModelRequest([
            SystemPromptPart(content=await self._state.get_system_prompt()),
            UserPromptPart(content=await self._state.get_intro_message()),
        ])

    async def append_messages(
        self,
        db_session: AsyncDbSession,
        model_messages: Iterable[ModelMessage],
        message_ids: Sequence[UUID] | None = None,
        part_ids: Sequence[Sequence[UUID]] | None = None,
        durations: dict[UUID, int] | None = None,
    ) -> None:
        messages: list[Message] = []

        for idx, model_message in enumerate(model_messages):
            model_msg_id: UUID | None = None
            model_part_ids: Sequence[UUID] | None = None
            if message_ids is not None:
                with suppress(IndexError):
                    model_msg_id = message_ids[idx]
            if part_ids is not None:
                with suppress(IndexError):
                    model_part_ids = part_ids[idx]
            msg = Message.from_model_message(
                model_message, self._session_id, model_msg_id, model_part_ids, durations
            )
            messages.append(msg)

        await create_messages(db_session, messages)

    async def create_user_request(
        self, db_session: AsyncDbSession, message_in: "ModelRequestCreate"
    ) -> Message:
        # Ensure UserPromptPart has a timestamp
        for p in message_in.parts:
            if p.part_kind == "user-prompt":
                p.timestamp = datetime.now(UTC)

        message = Message(
            **message_in.model_dump(exclude={"parts"}),
            session_id=self._session_id,
            parts=[Part(**p.model_dump()) for p in message_in.parts],
        )
        message = await create_message(db_session, message)
        self._bus.publish("engine.response.user_request", self._session_id)
        return message

    @property
    def session_id(self) -> UUID:
        return self._session_id
