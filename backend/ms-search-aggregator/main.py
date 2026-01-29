"""Search aggregator microservice with Redis caching."""

import json
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Path, Header, Depends

from utils.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    REDIS_CACHE_TTL,
    CACHE_ENABLED,
)
from models import AugmentedSearchResponse, ExistenceResponse
from services.search_orchestrator import search_and_augment_drops, aggregate_existence_by_name
from utils.auth import User, get_current_user
from utils.cache import CacheClient
from utils.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """
    Manage application lifespan for startup and shutdown events.

    Args:
        fastapi_app: FastAPI application instance.

    Yields:
        None after startup completes.
    """
    # Startup
    if CACHE_ENABLED:
        fastapi_app.state.cache = CacheClient(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            prefix="search",
            ttl=REDIS_CACHE_TTL,
        )
        await fastapi_app.state.cache.connect()
    else:
        fastapi_app.state.cache = None
        logger.info("Cache is disabled")

    yield

    # Shutdown
    if fastapi_app.state.cache:
        await fastapi_app.state.cache.close()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)


@app.get("/search/{name}")
async def search_with_cache(
    name: str,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Search for drops with Redis caching.

    Args:
        name: Name of the mob to search for.
        background_tasks: FastAPI background tasks for async caching.
        authorization: JWT authorization header for downstream calls.
        user: Current authenticated user.

    Returns:
        Aggregated search response with drop data.

    Raises:
        HTTPException: 500 if an internal error occurs.
    """
    logger.info("User %s searching for: %s", user.name, name)

    cache: CacheClient | None = app.state.cache
    cache_key = name

    # 1. Try cache first
    if cache and cache.is_connected:
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Cache hit for %s (user: %s)", name, user.name)
            return json.loads(cached_data.decode("utf-8"))

    logger.info("Cache miss for %s, fetching from aggregator (user: %s)", name, user.name)

    # 2. Fetch and aggregate data (pass authorization to downstream services)
    headers = {"Authorization": authorization}
    async with httpx.AsyncClient(headers=headers) as client:
        try:
            augmented_drops = await search_and_augment_drops(client, name)
            response_data = AugmentedSearchResponse(data=augmented_drops)
            result = response_data.model_dump()

            # 3. Cache in background (non-blocking)
            if cache and cache.is_connected:
                json_data = json.dumps(result).encode("utf-8")
                background_tasks.add_task(cache.set, cache_key, json_data)

            return result
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error during search for user %s: %s", user.name, e)
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            ) from e
        except httpx.RequestError as e:
            logger.error("Request error during search for user %s: %s", user.name, e)
            raise HTTPException(
                status_code=500,
                detail="Error connecting to downstream service"
            ) from e


@app.get("/api/search/drops-augmented", response_model=AugmentedSearchResponse)
async def search_drops_augmented(
    name: str = Query(..., description="Name of the mob to search for."),
    authorization: str = Header(...),
    user: User = Depends(get_current_user),
) -> AugmentedSearchResponse:
    """
    Search for augmented drop data (internal API, no caching).

    Args:
        name: Name of the mob to search for.
        authorization: JWT authorization header for downstream calls.
        user: Current authenticated user.

    Returns:
        Augmented search response with drop data.

    Raises:
        HTTPException: On HTTP errors or internal errors.
    """
    logger.info("User %s requesting drops-augmented for: %s", user.name, name)

    headers = {"Authorization": authorization}
    async with httpx.AsyncClient(headers=headers) as client:
        try:
            augmented_drops = await search_and_augment_drops(client, name)
            return AugmentedSearchResponse(data=augmented_drops)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error for user %s: %s", user.name, e)
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            ) from e
        except httpx.RequestError as e:
            logger.error("Request error for user %s: %s", user.name, e)
            raise HTTPException(
                status_code=500,
                detail="An internal server error occurred."
            ) from e


@app.get("/api/existence-check/{name}", response_model=ExistenceResponse)
async def get_existence_check(
    name: str = Path(..., description="Name of the mob or item to check existence for."),
    authorization: str = Header(...),
    user: User = Depends(get_current_user),
) -> ExistenceResponse:
    """
    Check existence of images and database entries for a given name.

    Args:
        name: Name of the mob or item to check.
        authorization: JWT authorization header for downstream calls.
        user: Current authenticated user.

    Returns:
        Existence check response with image and drop status.

    Raises:
        HTTPException: On HTTP errors or internal errors.
    """
    logger.info("User %s checking existence for: %s", user.name, name)

    headers = {"Authorization": authorization}
    async with httpx.AsyncClient(headers=headers) as client:
        try:
            results = await aggregate_existence_by_name(client, name)
            return ExistenceResponse(results=results)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error for user %s: %s", user.name, e)
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            ) from e
        except httpx.RequestError as e:
            logger.error("Request error for user %s: %s", user.name, e)
            raise HTTPException(
                status_code=500,
                detail="An internal server error occurred."
            ) from e


@app.get("/health/ready")
async def readiness() -> dict:
    """
    Readiness probe endpoint.

    Checks if cache dependency is available (when enabled).

    Returns:
        Status dict with dependency states.
    """
    cache: CacheClient | None = app.state.cache

    cache_status = "disabled"
    if CACHE_ENABLED:
        if cache and cache.is_connected:
            cache_status = "connected"
        else:
            cache_status = "disconnected"

    return {
        "status": "ready",
        "cache": cache_status,
    }
