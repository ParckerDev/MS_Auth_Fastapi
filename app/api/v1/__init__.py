from fastapi import APIRouter

from app.core import settings
from app.api.v1.item_api import router as item_router
from app.api.v1.healthcheck_api import router as healthcheck_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(router=healthcheck_router)
router.include_router(router=item_router)
