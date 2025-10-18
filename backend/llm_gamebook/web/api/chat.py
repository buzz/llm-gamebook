from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import func, select

from llm_gamebook.db.chat import Chat

from .deps import DbSessionDep, EngineDepRest
from .models import ChatCreate, ChatPublic, ChatsPublic, ServerMessage

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/")
async def read_chats(session: DbSessionDep, skip: int = 0, limit: int = 100) -> ChatsPublic:
    statement = select(Chat).offset(skip).limit(limit)
    count_statement = select(func.count()).select_from(Chat)
    return ChatsPublic(
        data=(await session.exec(statement)).all(),
        count=(await session.exec(count_statement)).one(),
    )


@router.get("/{chat_id}", response_model=ChatPublic)
async def read_chat(engine: EngineDepRest) -> Chat:
    chat = await engine.get_chat()
    # chat = await session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Story chat not found")
    return chat


@router.post("/", response_model=ChatPublic)
async def create_chat(session: DbSessionDep, chat_in: ChatCreate) -> Chat:
    chat = Chat.model_validate(chat_in)
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat


@router.delete("/{chat_id}")
async def delete_chat(session: DbSessionDep, chat_id: UUID) -> ServerMessage:
    chat = await session.get(Chat, chat_id)
    await session.delete(chat)
    await session.commit()
    return ServerMessage(message="Story chat deleted successfully.")
