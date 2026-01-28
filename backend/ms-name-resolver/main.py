"""Name resolver microservice for MongoDB ID-name lookups."""

import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from models import (
    ResolveNamesRequest,
    ResolveNamesResponse,
    ResolveIdsRequest,
    ResolveIdsResponse,
    GetAllNamesResponse,
    NameIdType,
)
from utils.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:20000/?directConnection=true")
DB_NAME = "maplestory"
COLLECTION_NAME = "name"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
logger.info("Connected to MongoDB at %s, database '%s', collection '%s'", MONGO_URI, DB_NAME, COLLECTION_NAME)

app = FastAPI()
app.include_router(health_router)

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

    Args:
        name: Name to look up.

    Returns:
        List of NameIdType objects with matching IDs and types.
    """
    logger.info("Received request to get IDs for name: %s", name)

    cursor = collection.find({"name": name}, {"_id": 0, "id": 1, "type": 1})

    result = []
    for doc in cursor:
        result.append(NameIdType(id=doc["id"], type=doc["type"]))

    logger.info("Found %d entries for name '%s'", len(result), name)
    return result


@app.get("/health/ready")
async def readiness() -> dict:
    """
    Readiness probe endpoint.

    Checks if MongoDB dependency is available.

    Returns:
        Status dict with dependency states.

    Raises:
        HTTPException: 503 if MongoDB is unavailable.
    """
    try:
        client.admin.command("ping")
    except PyMongoError as e:
        logger.error("MongoDB health check failed: %s", e)
        raise HTTPException(status_code=503, detail="MongoDB unavailable") from e

    return {
        "status": "ready",
        "mongodb": "connected",
    }

