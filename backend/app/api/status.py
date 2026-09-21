from fastapi import APIRouter
from app.core.settings import settings

router = APIRouter()

@router.get("/v1/status")
async def get_status():
    return {
        "llm_mode": settings.llm_mode,
        "capacity": "OK" # Can be wired to ResilientClient breaker state later
    }
