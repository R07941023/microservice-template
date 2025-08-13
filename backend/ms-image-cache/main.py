from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
import os
import logging
import redis
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Redis Connection ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_CACHE_EXPIRATION_SECONDS = int(os.getenv("REDIS_CACHE_EXPIRATION_SECONDS", 3600))


try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD
    )
    redis_client.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    redis_client = None

# --- Image Retriever Service URL ---
IMAGE_RETRIEVER_URL = os.getenv("IMAGE_RETRIEVER_URL", "http://ms-image-retriever:8000")

# --- API Endpoints ---
@app.get("/images/{type}/{dropper_id}")
async def get_image(type: str, dropper_id: str):
    image_key = f"image:{type}:{dropper_id}"

    # 1. Try to get image from Redis
    if redis_client:
        try:
            cached_image = redis_client.get(image_key)
            if cached_image:
                logger.info(f"Image {image_key} found in Redis cache.")
                return Response(content=cached_image, media_type="image/png")
        except Exception as e:
            logger.error(f"Error retrieving image from Redis: {e}")

    # 2. If not in Redis, fetch from ms-image-retriever
    logger.info(f"Image {image_key} not in cache. Fetching from {IMAGE_RETRIEVER_URL}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{IMAGE_RETRIEVER_URL}/images/{type}/{dropper_id}")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            image_data = response.content

            # 3. Store in Redis for future requests
            if redis_client:
                try:
                    # Cache for 1 hour (3600 seconds)
                    redis_client.setex(image_key, REDIS_CACHE_EXPIRATION_SECONDS, image_data)
                    logger.info(f"Image {image_key} cached in Redis.")
                except Exception as e:
                    logger.error(f"Error caching image in Redis: {e}")

            return Response(content=image_data, media_type="image/png")

        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching image from image-retriever: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Image not found or error from retriever: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Network error or invalid URL for image-retriever: {e}")
            raise HTTPException(status_code=500, detail=f"Could not connect to image retriever service: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
