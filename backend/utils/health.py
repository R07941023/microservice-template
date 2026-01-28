"""Common health check endpoints for microservices."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict:
    """
    Liveness probe endpoint.

    Checks if the service process is running.
    Always returns 200 if the service can respond.

    Returns:
        Status dict indicating service is alive.
    """
    return {"status": "alive"}
