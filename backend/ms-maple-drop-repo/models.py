from pydantic import BaseModel
from typing import List, Literal

# --- Pydantic Models for Drop CRUD ---
class DropUpdate(BaseModel):
    dropperid: int
    itemid: int
    minimum_quantity: int
    maximum_quantity: int
    questid: int
    chance: int

class DropCreate(BaseModel):
    dropperid: int
    itemid: int
    minimum_quantity: int
    maximum_quantity: int
    questid: int
    chance: int

# --- Pydantic Models for Existence Check ---
class ExistenceInfo(BaseModel):
    type: Literal["mob", "item"]
    id: int

class ExistenceCheckRequest(BaseModel):
    items: List[ExistenceInfo]

class ExistenceResult(BaseModel):
    type: Literal["mob", "item"]
    id: int
    drop_exist: bool

class ExistenceCheckResponse(BaseModel):
    results: List[ExistenceResult]
