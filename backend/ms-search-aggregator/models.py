from pydantic import BaseModel
from typing import List, Dict, Any, Literal

class AugmentedDrop(BaseModel):
    id: str
    dropperid: int
    dropper_name: str
    itemid: int
    item_name: str
    minimum_quantity: int
    maximum_quantity: int
    questid: int
    chance: int

class AugmentedSearchResponse(BaseModel):
    data: List[AugmentedDrop]

class IdInfo(BaseModel):
    id: int
    type: Literal["item", "mob"]
