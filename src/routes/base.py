from fastapi import APIRouter

base_router = APIRouter()


@base_router.get("/health")
async def health_check():
    return {"status": "ok"}
