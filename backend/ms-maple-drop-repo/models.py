from pydantic import BaseModel

# --- Pydantic Models ---
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
