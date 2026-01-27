import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
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
        "IMAGE_RETRIEVER_URL": "http://mock-image-retriever:8000"
    }):
        with patch("redis.Redis", return_value=mock_redis_client):
            with patch("main.redis_client", mock_redis_client):
                from main import app
                with TestClient(app) as test_client:
                    yield test_client


@pytest.fixture
def sample_image_data():
    """Sample PNG image data."""
    # Minimal valid PNG bytes
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
