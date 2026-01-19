from fastapi import FastAPI
from typing import List, Dict
import os
from pymongo import MongoClient
import logging
from models import ResolveNamesRequest, ResolveNamesResponse, ResolveIdsRequest, ResolveIdsResponse, GetAllNamesResponse, NameIdType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- MongoDB Connection ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:20000/?directConnection=true")
DB_NAME = "maplestory"
COLLECTION_NAME = "name"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
logger.info(f"Connected to MongoDB at {MONGO_URI}, using database '{DB_NAME}' and collection '{COLLECTION_NAME}'")

# --- API Endpoints ---
@app.post("/api/id-names/resolve", response_model=ResolveNamesResponse)
async def resolve_names(request: ResolveNamesRequest):
    
    # Query for item names
    item_cursor = collection.find({
        "id": {"$in": request.idList},
        "type": request.type
    })
    names={str(doc["id"]): doc["name"] for doc in item_cursor}
    
    return ResolveNamesResponse(names=names)

@app.post("/api/names-id/resolve", response_model=ResolveIdsResponse)
async def resolve_ids(request: ResolveIdsRequest):
    
    # Query for item names
    item_cursor = collection.find({
        "name": {"$in": request.nameList},
    })
    ids = {
        doc["name"]: {"id": doc["id"], "type": doc["type"]}
        for doc in item_cursor
    }
    
    return ResolveIdsResponse(ids=ids)

@app.get("/api/names/all", response_model=GetAllNamesResponse)
async def get_all_names():
    # Query for all unique names in the collection
    names = collection.distinct("name")
    return GetAllNamesResponse(names=names)

@app.get("/api/name-to-ids/{name}", response_model=List[NameIdType])
async def get_ids_by_name(name: str):
    """
    Get all IDs, names, and types associated with a specific name.
    """
    logger.info(f"Received request to get IDs for name: {name}")
    
    # Query for all documents matching the name
    # Explicitly project the _id field to exclude it or include if needed
    cursor = collection.find({"name": name}, {"_id": 0, "id": 1, "type": 1})
    
    # Construct a list of NameIdType objects
    result = []
    for doc in cursor:
        result.append(NameIdType(id=doc["id"], type=doc["type"]))
    
    logger.info(f"Found {len(result)} entries for name '{name}': {result}")
    return result

