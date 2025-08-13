from fastapi import FastAPI, HTTPException
import redis
import httpx
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_CACHE_EXPIRATION_SECONDS = int(os.getenv("REDIS_CACHE_EXPIRATION_SECONDS", 3600)) # Cache for 1 hour
AUGMENTED_SERVICE_URL = os.getenv("AUGMENTED_SERVICE_URL", "http://ms-search-aggregator:8000/api/search/drops-augmented")

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

@app.get("/search/{name}")
async def search_with_cache(name: str):
    cache_key = f"search:{name}"
    
    # Try to get from cache
    cached_result = redis_client.get(cache_key)
    if cached_result:
        print(f"Cache hit for {name}")
        return {"source": "cache", "data": cached_result.decode('utf-8')} # Assuming JSON string
    
    print(f"Cache miss for {name}, fetching from aggregator")
    
    # If not in cache, fetch from ms-search-aggregator
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                AUGMENTED_SERVICE_URL,
                params={"name": name}
            )
            response.raise_for_status()
            aggregator_data = response.json()
            
            # Cache the result
            redis_client.setex(cache_key, REDIS_CACHE_EXPIRATION_SECONDS, response.text)
            
            return {"source": "aggregator", "data": aggregator_data}
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to search aggregator: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from search aggregator: {e.response.text}")

@app.get("/health")
async def health_check():
    try:
        redis_client.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {e}")
