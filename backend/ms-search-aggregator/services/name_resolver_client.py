from typing import List, Dict
import httpx
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NAME_RESOLVER_URL = "http://ms-name-resolver:8000"

async def resolve_name_to_id(client: httpx.AsyncClient, name: str) -> int | None:
    """Resolves a single name to an ID."""
    try:
        response = await client.post(f"{NAME_RESOLVER_URL}/api/names-id/resolve", json={"nameList": [name]})
        response.raise_for_status()
        resolved_ids = response.json().get('ids', {})
        return resolved_ids.get(name)
    except httpx.HTTPStatusError as e:
        logger.error(f"Error resolving name to ID: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while resolving name to ID: {e}", exc_info=True)
        raise

async def resolve_ids_to_names(client: httpx.AsyncClient, ids: List[int], id_type: str) -> Dict[str, str]:
    """Resolves a list of IDs to their corresponding names."""
    if not ids:
        return {}
    try:
        response = await client.post(f"{NAME_RESOLVER_URL}/api/id-names/resolve", json={"idList": ids, "type": id_type})
        response.raise_for_status()
        return response.json().get('names', {})
    except httpx.HTTPStatusError as e:
        logger.error(f"Error resolving IDs to names: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while resolving IDs to names: {e}", exc_info=True)
        raise
