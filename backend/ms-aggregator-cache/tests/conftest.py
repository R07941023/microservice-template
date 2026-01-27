import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    client = MagicMock()
    client.ping.return_value = True
    client.get.return_value = None
    client.setex.return_value = True
    return client


@pytest.fixture
def client(mock_redis_client):
    """Create a FastAPI test client with mocked dependencies."""
    with patch.dict(os.environ, {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
        "REDIS_PASSWORD": "",
        "REDIS_CACHE_EXPIRATION_SECONDS": "3600",
        "AUGMENTED_SERVICE_URL": "http://mock-aggregator:8000/api/search/drops-augmented"
    }):
        with patch("redis.Redis", return_value=mock_redis_client):
            with patch("main.redis_client", mock_redis_client):
                from main import app
                with TestClient(app) as test_client:
                    yield test_client


@pytest.fixture
def sample_search_result():
    """Sample search result from aggregator."""
    return {
        "data": [
            {
                "id": "1",
                "dropperid": 100100,
                "dropper_name": "Snail",
                "itemid": 2000001,
                "item_name": "Red Potion",
                "minimum_quantity": 1,
                "maximum_quantity": 1,
                "questid": 0,
                "chance": 100000
            }
        ]
    }


@pytest.fixture
def valid_jwt_token():
    """Create a valid JWT token for testing."""
    import jwt
    payload = {"name": "Test User", "email": "test@example.com"}
    return "Bearer " + jwt.encode(payload, "secret", algorithm="HS256")
