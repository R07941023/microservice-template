from fastapi import FastAPI
from typing import List, Dict
import os
from pymongo import MongoClient
import logging
from models import ResolveNamesRequest, ResolveNamesResponse, ResolveIdsRequest, ResolveIdsResponse

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

