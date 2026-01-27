import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_cursor():
    """Create a mock database cursor."""
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.lastrowid = 1
    cursor.rowcount = 1
    return cursor


@pytest.fixture
def mock_writer_cursor():
    """Create a mock database writer cursor."""
    cursor = MagicMock()
    cursor.lastrowid = 1
    cursor.rowcount = 1
    return cursor


@pytest.fixture
def client(mock_cursor, mock_writer_cursor):
    """Create a FastAPI test client with mocked database connections."""
    with patch.dict(os.environ, {
        "MYSQL_HOST": "localhost:3306",
        "MYSQL_USER": "test_user",
        "MYSQL_PASSWORD": "test_password",
        "MYSQL_DATABASE": "test_db"
    }):
        with patch("mysql.connector.pooling.MySQLConnectionPool"):
            from main import app, get_db_cursor, get_db_writer_cursor

            def override_get_db_cursor():
                yield mock_cursor

            def override_get_db_writer_cursor():
                yield mock_writer_cursor

            app.dependency_overrides[get_db_cursor] = override_get_db_cursor
            app.dependency_overrides[get_db_writer_cursor] = override_get_db_writer_cursor

            with TestClient(app) as test_client:
                yield test_client

            app.dependency_overrides.clear()


@pytest.fixture
def sample_drop_data():
    """Sample drop data for testing."""
    return {
        "dropperid": 100100,
        "itemid": 2000001,
        "minimum_quantity": 1,
        "maximum_quantity": 5,
        "questid": 0,
        "chance": 100000
    }


@pytest.fixture
def sample_drop_record():
    """Sample drop record as returned from database."""
    return {
        "id": 1,
        "dropperid": 100100,
        "itemid": 2000001,
        "minimum_quantity": 1,
        "maximum_quantity": 5,
        "questid": 0,
        "chance": 100000
    }
