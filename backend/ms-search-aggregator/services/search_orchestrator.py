from typing import List, Dict, Any
import httpx
import asyncio
import logging
from models import AugmentedDrop
from . import name_resolver_client, drop_repo_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def search_and_augment_drops(client: httpx.AsyncClient, name: str) -> List[AugmentedDrop]:
    """
    Orchestrates the process of searching for drop data, resolving names,
    generating image URLs, and augmenting the final results.
    """
    idInfo = await name_resolver_client.resolve_name_to_id(client, name)
    if not idInfo:
        return []

    drops = await drop_repo_client.fetch_drops_by_mob_id(client, idInfo)
    if not drops:
        return []

    dropper_ids = list(set(d['dropperid'] for d in drops))
    item_ids = list(set(d['itemid'] for d in drops))

    # Concurrently resolve names and generate image URLs
    dropper_names_task = name_resolver_client.resolve_ids_to_names(client, dropper_ids, "mob")
    item_names_task = name_resolver_client.resolve_ids_to_names(client, item_ids, "item")
    
    # Await the name resolution tasks
    dropper_names, item_names = await asyncio.gather(dropper_names_task, item_names_task)

    # Directly augment the drop data in the final step
    return [
        AugmentedDrop(
            **d,
            dropper_name=dropper_names.get(str(d['dropperid']), "Unknown"),
            item_name=item_names.get(str(d['itemid']), "Unknown"),
        ) for d in drops
    ]
