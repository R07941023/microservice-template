from fastapi import FastAPI, HTTPException, Query, Path
import httpx
import logging
from models import AugmentedSearchResponse, ExistenceResponse
from services.search_orchestrator import search_and_augment_drops, aggregate_existence_by_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/api/search/drops-augmented", response_model=AugmentedSearchResponse)
async def search_drops_augmented(name: str = Query(..., description="Name of the mob to search for.")):
    async with httpx.AsyncClient() as client:
        try:
            augmented_drops = await search_and_augment_drops(client, name)
            return AugmentedSearchResponse(data=augmented_drops)

        except httpx.HTTPStatusError as e:
            # The client functions will log the specifics, so we just re-raise
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main endpoint: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/api/existence-check/{name}", response_model=ExistenceResponse)
async def get_existence_check(name: str = Path(..., description="Name of the mob or item to check existence for.")):
    async with httpx.AsyncClient() as client:
        try:
            results = await aggregate_existence_by_name(client, name)
            return ExistenceResponse(results=results)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            logger.error(f"An unexpected error occurred in existence check endpoint: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An internal server error occurred.")

