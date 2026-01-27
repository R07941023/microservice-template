import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    return collection


@pytest.fixture
def mock_mongo_client(mock_collection):
    """Create a mock MongoDB client."""
    client = MagicMock()
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=mock_collection)
    client.__getitem__ = MagicMock(return_value=db)
    return client


@pytest.fixture
def client(mock_collection, mock_mongo_client):
    """Create a FastAPI test client with mocked dependencies."""
    with patch.dict(os.environ, {
        "MONGO_URI": "mongodb://localhost:27017"
    }):
        with patch("pymongo.MongoClient", return_value=mock_mongo_client):
            with patch("main.collection", mock_collection):
                from main import app
                with TestClient(app) as test_client:
                    yield test_client


@pytest.fixture
def sample_mob_docs():
    """Sample mob documents."""
    return [
        {"id": 100100, "name": "Snail", "type": "mob"},
        {"id": 100101, "name": "Blue Snail", "type": "mob"}
    ]


@pytest.fixture
def sample_item_docs():
    """Sample item documents."""
    return [
        {"id": 2000001, "name": "Red Potion", "type": "item"},
        {"id": 2000002, "name": "Blue Potion", "type": "item"}
    ]
