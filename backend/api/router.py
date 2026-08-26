from fastapi import APIRouter

from backend.api.v1.controls import router as controls_router
from backend.api.v1.frameworks import router as frameworks_router

api_router = APIRouter()
api_router.include_router(frameworks_router)
api_router.include_router(controls_router)
