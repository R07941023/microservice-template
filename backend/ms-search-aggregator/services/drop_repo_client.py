"""Client for ms-maple-drop-repo service."""

import logging
from typing import Any, Dict, List

import httpx

from models import IdInfo

logger = logging.getLogger(__name__)

DROP_REPO_URL = "http://ms-maple-drop-repo:8000"


async def fetch_drops_by_mob_id(
    client: httpx.AsyncClient, idInfo: IdInfo
) -> List[Dict[str, Any]]:
    """
    Fetch drop data for a given mob ID from the drop-repo service.

    Args:
        client: HTTP client with authorization headers.
        idInfo: ID info containing id and type.

    Returns:
        List of drop data dictionaries.

    Raises:
        httpx.HTTPStatusError: On HTTP errors.
        httpx.RequestError: On connection errors.
    """
    try:
        response = await client.get(
            f"{DROP_REPO_URL}/api/search_drops",
            params={"query": idInfo["id"], "query_type": idInfo["type"]}
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("Error fetching drops: %s - %s", e.response.status_code, e.response.text)
        raise
    except httpx.RequestError as e:
        logger.error("Connection error while fetching drops: %s", e)
        raise


async def check_drops_exist(client: httpx.AsyncClient, items: List[Dict]) -> List[Dict]:
    """
    Check for the existence of multiple drops.

    Args:
        client: HTTP client with authorization headers.
        items: List of items to check.

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
            f"{DROP_REPO_URL}/api/drops/exist",
            json={"items": items}
        )
        response.raise_for_status()
        return response.json().get('results', [])
    except httpx.HTTPStatusError as e:
        logger.error("Error checking drop existence: %s - %s", e.response.status_code, e.response.text)
        raise
    except httpx.RequestError as e:
        logger.error("Connection error while checking drop existence: %s", e)
        raise
