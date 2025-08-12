from typing import List, Dict, Any, TypedDict, Literal
import httpx
import logging
from models import IdInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DROP_REPO_URL = "http://ms-maple-drop-repo:8000"

async def fetch_drops_by_mob_id(client: httpx.AsyncClient, idInfo: IdInfo) -> List[Dict[str, Any]]:
    """Fetches drop data for a given mob ID from the drop-repo service."""
    try:
        response = await client.get(f"{DROP_REPO_URL}/api/search_drops", params={"query": idInfo["id"], "query_type": idInfo["type"]})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching drops: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching drops: {e}", exc_info=True)
        raise
