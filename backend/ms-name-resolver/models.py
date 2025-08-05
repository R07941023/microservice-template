from pydantic import BaseModel
from typing import List, Dict

# --- Pydantic Models for resolving names from IDs ---
class ResolveNamesRequest(BaseModel):
    idList: List[int]
    type: str

class ResolveNamesResponse(BaseModel):
    names: Dict[str, str]

# --- Pydantic Models for resolving IDs from names ---
class ResolveIdsRequest(BaseModel):
    nameList: List[str]

class ResolveIdsResponse(BaseModel):
    ids: Dict[str, int]