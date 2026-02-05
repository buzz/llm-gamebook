from fastapi import APIRouter

from .model_config_router import model_config_router
from .session_router import session_router

api_router = APIRouter()
api_router.include_router(model_config_router)
api_router.include_router(session_router)
