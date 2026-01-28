"""Image retriever microservice with Redis caching."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from minio.error import S3Error

from config import MINIO_BUCKET, MINIO_ENDPOINT, THREAD_POOL_SIZE
from utils.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    REDIS_CACHE_TTL,
    CACHE_ENABLED,
)
from models import ImageCheckRequest, ImageCheckResponse, ImageInfo, ImageExistence
from services import minio_service
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
    logger.info("Connected to MinIO at %s", MINIO_ENDPOINT)
    logger.info("Thread pool size: %s", THREAD_POOL_SIZE)

    if CACHE_ENABLED:
        fastapi_app.state.cache = CacheClient(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            prefix="image",
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
    minio_service.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)


@app.get("/images/{image_type}/{dropper_id}")
async def get_image(
    image_type: str,
    dropper_id: str,
    background_tasks: BackgroundTasks
) -> Response:
    """
    Retrieve an image by type and dropper ID.

    Checks Redis cache first, falls back to MinIO if not cached.
    Caches the result in background after fetching from MinIO.

    Args:
        image_type: Image type category.
        dropper_id: Unique identifier for the dropper.
        background_tasks: FastAPI background tasks for async caching.

    Returns:
        PNG image response.

    Raises:
        HTTPException: 404 if image not found in MinIO.
    """
    cache: CacheClient | None = app.state.cache
    cache_key = f"{image_type}:{dropper_id}"

    # 1. Try cache first
    if cache and cache.is_connected:
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("Cache hit for %s", cache_key)
            return Response(content=cached_data, media_type="image/png")

    # 2. Fetch from MinIO
    object_name = f"{image_type}/{dropper_id}.png"

    try:
        data = await minio_service.fetch_image(MINIO_BUCKET, object_name)
        logger.info("Fetched %s from MinIO", object_name)

        # 3. Cache in background (non-blocking)
        if cache and cache.is_connected:
            background_tasks.add_task(cache.set, cache_key, data)

        return Response(content=data, media_type="image/png")
    except S3Error as e:
        logger.error("Error retrieving image '%s': %s", object_name, e)
        raise HTTPException(status_code=404, detail="Image not found") from e


@app.post("/api/images/exist", response_model=ImageCheckResponse)
async def check_images_exist(request: ImageCheckRequest) -> ImageCheckResponse:
    """
    Check if multiple images exist in MinIO storage.

    Args:
        request: Request containing list of images to check.

    Returns:
        Response with existence status for each image.
    """
    async def check_single(image_info: ImageInfo) -> ImageExistence:
        """Check single image existence."""
        object_name = f"{image_info.type}/{image_info.dropper_id}.png"
        exists = await minio_service.check_object_exists(MINIO_BUCKET, object_name)
        return ImageExistence(
            dropper_id=image_info.dropper_id,
            type=image_info.type,
            exists=exists
        )

    tasks = [check_single(image_info) for image_info in request.images]
    results = await asyncio.gather(*tasks)
    return ImageCheckResponse(results=list(results))


@app.get("/health/ready")
async def readiness() -> dict:
    """
    Readiness probe endpoint.

    Checks if MinIO dependency is available.

    Returns:
        Status dict with dependency states.

    Raises:
        HTTPException: 503 if MinIO is unavailable.
    """
    cache: CacheClient | None = app.state.cache

    try:
        await minio_service.check_bucket_exists(MINIO_BUCKET)
    except S3Error as e:
        logger.error("MinIO health check failed: %s", e)
        raise HTTPException(status_code=503, detail="MinIO unavailable") from e

    cache_status = "disabled"
    if CACHE_ENABLED:
        cache_status = "connected" if cache and cache.is_connected else "disconnected"

    return {
        "status": "ready",
        "minio": "connected",
        "cache": cache_status,
    }
