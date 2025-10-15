import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from llm_gamebook.db.chat import Chat, ChatCreate, ChatPublic, ChatsPublic
from llm_gamebook.webui.api.deps import SessionDep

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/")
async def read_chats(session: SessionDep, skip: int = 0, limit: int = 100) -> ChatsPublic:
    count_statement = select(func.count()).select_from(Chat)
    count = session.exec(count_statement).one()
    statement = select(Chat).offset(skip).limit(limit)
    chats = session.exec(statement).all()
    return ChatsPublic(data=chats, count=count)


@router.get("/{chat_id}", response_model=ChatPublic)
async def read_chat(session: SessionDep, chat_id: uuid.UUID) -> Chat:
    chat = session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Item not found")
    return chat


@router.post("/{chat_id}", response_model=ChatPublic)
async def create_chat(session: SessionDep, chat_in: ChatCreate) -> Chat:
    chat = Chat.model_validate(chat_in)
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat
