"""Client for ms-image-retriever service."""

import logging
from typing import Dict, List

import httpx

logger = logging.getLogger(__name__)

IMAGE_RETRIEVER_URL = "http://ms-image-retriever:8000"


async def check_images_exist(client: httpx.AsyncClient, items: List[Dict]) -> List[Dict]:
    """
    Check for the existence of multiple images.

    Args:
        client: HTTP client with authorization headers.
        items: List of image items to check.

    Returns:
        List of existence check results.

    Raises:
        httpx.HTTPStatusError: On HTTP errors.
        httpx.RequestError: On connection errors.
    """
    if not items:
        return []
    try:
        response = await client.post(
            f"{IMAGE_RETRIEVER_URL}/api/images/exist",
            json={"images": items}
        )
        response.raise_for_status()
        return response.json().get('results', [])
    except httpx.HTTPStatusError as e:
        logger.error("Error checking image existence: %s - %s", e.response.status_code, e.response.text)
        raise
    except httpx.RequestError as e:
        logger.error("Connection error while checking image existence: %s", e)
        raise
