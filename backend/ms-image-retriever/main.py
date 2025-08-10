from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from minio import Minio
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- MinIO Connection ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minio")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minio")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "minio")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)

logger.info(f"Connected to MinIO at {MINIO_ENDPOINT}")

# --- API Endpoints ---
@app.get("/images/{type}/{dropper_id}")
async def get_image(type: str, dropper_id: str):
    object_name = f"{type}/{dropper_id}.png"
    try:
        # Get object data from MinIO
        response = minio_client.get_object(MINIO_BUCKET, object_name)
        
        # Stream the image back to the client
        return StreamingResponse(response.stream(32*1024), media_type="image/png")
    except Exception as e:
        # Log the error and return 404 if image not found
        logger.error(f"Error retrieving image '{object_name}': {e}")
        raise HTTPException(status_code=404, detail="Image not found")
    finally:
        # Ensure the connection is released
        if 'response' in locals() and response:
            response.close()
            response.release_conn()
