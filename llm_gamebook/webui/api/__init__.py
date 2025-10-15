from fastapi import APIRouter

from llm_gamebook.webui.api import chat, websocket

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(websocket.router)
