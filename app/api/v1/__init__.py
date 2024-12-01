from fastapi import APIRouter

from .routes.insurance_calc import router as insurance_router
from .routes.administration import router as admin_router

router = APIRouter(prefix="/v1")

router.include_router(insurance_router)
router.include_router(admin_router)
