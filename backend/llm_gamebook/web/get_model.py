from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from pydantic_ai.models import Model
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState

from .model_factory import create_model_from_db_config


# TODO: move to engine manager?
async def get_model_state(db_session: AsyncDbSession, session_id: UUID) -> tuple[Model, StoryState]:
    path = Path(Path.home() / "llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
    state = StoryState(Project.from_path(path))

    statement = select(Session).where(Session.id == session_id)
    statement = statement.options(selectinload(Session.config))  # type: ignore[arg-type]
    result = await db_session.exec(statement)
    session = result.one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Story session not found")

    if not session.config:
        raise HTTPException(status_code=404, detail="Session has no model config")

    model = create_model_from_db_config(
        model_name=session.config.model_name,
        provider=session.config.provider,
        base_url=session.config.base_url,
        api_key=session.config.api_key,
    )

    return model, state
