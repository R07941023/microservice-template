from typing import List, Dict
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_RETRIEVER_URL = "http://ms-image-retriever:8000"

async def check_images_exist(client: httpx.AsyncClient, items: List[Dict]) -> List[Dict]:
    """Checks for the existence of multiple images."""
    if not items:
        return []
    try:
        # The request body for ms-image-retriever should be {"images": items}
        response = await client.post(f"{IMAGE_RETRIEVER_URL}/api/images/exist", json={"images": items})
        response.raise_for_status()
        return response.json().get('results', [])
    except httpx.HTTPStatusError as e:
        logger.error(f"Error checking image existence: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking image existence: {e}", exc_info=True)
        raise
