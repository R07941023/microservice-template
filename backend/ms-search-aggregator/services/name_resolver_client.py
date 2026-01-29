"""Client for ms-name-resolver service."""

import logging
from typing import Dict, List

import httpx

logger = logging.getLogger(__name__)

NAME_RESOLVER_URL = "http://ms-name-resolver:8000"


async def resolve_name_to_id(client: httpx.AsyncClient, name: str) -> dict | None:
    """
    Resolve a single name to an ID.

    Args:
        client: HTTP client with authorization headers.
        name: Name to resolve.

    Returns:
        ID info dict or None if not found.

    Raises:
        httpx.HTTPStatusError: On HTTP errors.
    """
    try:
        response = await client.post(
            f"{NAME_RESOLVER_URL}/api/names-id/resolve",
            json={"nameList": [name]}
        )
        response.raise_for_status()
        resolved_ids = response.json().get("ids", {})
        return resolved_ids.get(name)
    except httpx.HTTPStatusError as e:
        logger.error("Error resolving name to ID: %s - %s", e.response.status_code, e.response.text)
        raise


async def resolve_ids_to_names(
    client: httpx.AsyncClient,
    ids: List[int],
    id_type: str
) -> Dict[str, str]:
    """
    Resolve a list of IDs to their corresponding names.

    Args:
        client: HTTP client with authorization headers.
        ids: List of IDs to resolve.
        id_type: Type of IDs (mob or item).

    Returns:
        Dict mapping ID strings to names.

    Raises:
        httpx.HTTPStatusError: On HTTP errors.
    """
    if not ids:
        return {}
    try:
        response = await client.post(
            f"{NAME_RESOLVER_URL}/api/id-names/resolve",
            json={"idList": ids, "type": id_type}
        )
        response.raise_for_status()
        return response.json().get("names", {})
    except httpx.HTTPStatusError as e:
        logger.error("Error resolving IDs to names: %s - %s", e.response.status_code, e.response.text)
        raise


async def get_ids_for_name(client: httpx.AsyncClient, name: str) -> List[Dict]:
    """
    Get all ID/type pairs for a given name.

    Args:
        client: HTTP client with authorization headers.
        name: Name to look up.

    Returns:
        List of dicts with id and type.

    Raises:
        httpx.HTTPStatusError: On HTTP errors.
    """
    if not name:
        return []
    try:
        response = await client.get(f"{NAME_RESOLVER_URL}/api/name-to-ids/{name}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("Error getting IDs for name: %s - %s", e.response.status_code, e.response.text)
        raise
