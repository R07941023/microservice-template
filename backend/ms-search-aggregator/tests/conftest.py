import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    from main import app
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_drops():
    """Sample drop data."""
    return [
        {
            "id": "1",
            "dropperid": 100100,
            "itemid": 2000001,
            "minimum_quantity": 1,
            "maximum_quantity": 1,
            "questid": 0,
            "chance": 100000
        },
        {
            "id": "2",
            "dropperid": 100100,
            "itemid": 2000002,
            "minimum_quantity": 1,
            "maximum_quantity": 5,
            "questid": 0,
            "chance": 50000
        }
    ]


@pytest.fixture
def sample_augmented_drops():
    """Sample augmented drop data."""
    return [
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


@pytest.fixture
def sample_name_id_results():
    """Sample name to ID results."""
    return [
        {"type": "mob", "id": 100100},
        {"type": "item", "id": 2000001}
    ]
