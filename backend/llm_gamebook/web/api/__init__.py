from fastapi import APIRouter

from llm_gamebook.web.api import session, websocket

api_router = APIRouter()
api_router.include_router(session.router)
api_router.include_router(websocket.router)
