from fastapi import APIRouter

from .routes.logs import router as logs_router

router = APIRouter(prefix="/v1")

router.include_router(logs_router)
