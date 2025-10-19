from fastapi import APIRouter

from app.core import settings
from app.api.v1 import router as api_v1

router = APIRouter(prefix=settings.api.prefix)
router.include_router(router=api_v1)