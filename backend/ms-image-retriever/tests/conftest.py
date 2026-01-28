import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_minio_client():
    """Create a mock MinIO client."""
    client = MagicMock()
    return client


@pytest.fixture
def client(mock_minio_client):
    """Create a FastAPI test client with mocked dependencies."""
    with patch.dict(os.environ, {
        "MINIO_ENDPOINT": "localhost:9000",
        "MINIO_ROOT_USER": "test_user",
        "MINIO_ROOT_PASSWORD": "test_password",
        "MINIO_BUCKET": "test_bucket",
        "CACHE_ENABLED": "false",
    }):
        with patch("services.minio_service.minio_client", mock_minio_client):
            from main import app
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def sample_image_data():
    """Sample PNG image data."""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
