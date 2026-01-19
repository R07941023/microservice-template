from typing import List, Dict, Any
import httpx
import asyncio
import logging
from models import AugmentedDrop
from . import name_resolver_client, drop_repo_client, image_retriever_client

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

async def aggregate_existence_by_name(client: httpx.AsyncClient, name: str) -> List[Dict[str, Any]]:
    """
    Orchestrates checking for the existence of images and database entries for a given name.
    """
    # 1. Get all ID/Type pairs for the name
    name_id_results = await name_resolver_client.get_ids_for_name(client, name)
    if not name_id_results:
        return []

    # 2. Concurrently check for image and db existence
    image_exist_task = image_retriever_client.check_images_exist(client, name_id_results)
    db_exist_task = drop_repo_client.check_drops_exist(client, name_id_results)
    
    image_exist_results, db_exist_results = await asyncio.gather(image_exist_task, db_exist_task)

    # 3. Merge the results
    # Create a dictionary for quick lookup of existence status
    existence_map = {(item['type'], item['id']): {'image_exist': item.get('image_exist', False)} for item in image_exist_results}
    
    for item in db_exist_results:
        key = (item['type'], item['id'])
        if key in existence_map:
            existence_map[key]['drop_exist'] = item.get('drop_exist', False)
        else: # Handle cases where an item exists in DB but not in image results
            existence_map[key] = {'image_exist': False, 'drop_exist': item.get('drop_exist', False)}

    # 4. Format the final response
    final_results = [
        {
            "type": key[0],
            "id": key[1],
            **value
        }
        for key, value in existence_map.items()
    ]
    
    return final_results
