"""Search aggregator microservice with Redis caching."""

import json
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Path

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
from utils.cache import CacheClient
from utils.health import router as health_router

# Configure logging
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
    background_tasks: BackgroundTasks
) -> dict:
    """
    Search for drops with Redis caching.

    This is the main entry point for search queries.
    Checks cache first, falls back to aggregation if not cached.

    Args:
        name: Name of the mob to search for.
        background_tasks: FastAPI background tasks for async caching.

    Returns:
        Aggregated search response with drop data.

    Raises:
        HTTPException: 500 if an internal error occurs.
    """
    cache: CacheClient | None = app.state.cache
    cache_key = name

    # 1. Try cache first
    if cache and cache.is_connected:
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Cache hit for %s", name)
            return json.loads(cached_data.decode("utf-8"))

    logger.info("Cache miss for %s, fetching from aggregator", name)

    # 2. Fetch and aggregate data
    async with httpx.AsyncClient() as client:
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
            logger.error("HTTP error during search: %s", e)
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            ) from e
        except httpx.RequestError as e:
            logger.error("Request error during search: %s", e)
            raise HTTPException(
                status_code=500,
                detail="Error connecting to downstream service"
            ) from e


@app.get("/api/search/drops-augmented", response_model=AugmentedSearchResponse)
async def search_drops_augmented(
    name: str = Query(..., description="Name of the mob to search for.")
) -> AugmentedSearchResponse:
    """
    Search for augmented drop data (internal API, no caching).

    This endpoint is kept for backwards compatibility.
    For cached searches, use /search/{name} instead.

    Args:
        name: Name of the mob to search for.

    Returns:
        Augmented search response with drop data.

    Raises:
        HTTPException: On HTTP errors or internal errors.
    """
    async with httpx.AsyncClient() as client:
        try:
            augmented_drops = await search_and_augment_drops(client, name)
            return AugmentedSearchResponse(data=augmented_drops)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            ) from e
        except httpx.RequestError as e:
            logger.error("Request error in drops-augmented: %s", e)
            raise HTTPException(
                status_code=500,
                detail="An internal server error occurred."
            ) from e


@app.get("/api/existence-check/{name}", response_model=ExistenceResponse)
async def get_existence_check(
    name: str = Path(..., description="Name of the mob or item to check existence for.")
) -> ExistenceResponse:
    """
    Check existence of images and database entries for a given name.

    Args:
        name: Name of the mob or item to check.

    Returns:
        Existence check response with image and drop status.

    Raises:
        HTTPException: On HTTP errors or internal errors.
    """
    async with httpx.AsyncClient() as client:
        try:
            results = await aggregate_existence_by_name(client, name)
            return ExistenceResponse(results=results)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            ) from e
        except httpx.RequestError as e:
            logger.error("Request error in existence-check: %s", e)
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

    Raises:
        HTTPException: 503 if cache is enabled but unavailable.
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
