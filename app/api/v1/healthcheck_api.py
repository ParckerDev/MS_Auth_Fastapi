from fastapi import APIRouter

router = APIRouter(prefix="/healthcheck", tags=["HEALTHCHECK"])

@router.get("/")
async def healthcheck():
    return {"status": "ok"}