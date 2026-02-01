from fastapi import APIRouter

base_router = APIRouter(prefix="/api/v1",
                        tags=["Health"])

@base_router.get("/health")
async def health_check():
    """
    Simple endpoint to check if the API is running.
    Full URL: /api/v1/health
    """
    return {"status": "ok"}
