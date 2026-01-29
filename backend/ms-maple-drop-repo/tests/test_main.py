import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSearchDrops:
    """Tests for /api/search_drops endpoint."""

    def test_search_drops_by_item(self, client, mock_cursor, sample_drop_record):
        """Test searching drops by item ID."""
        mock_cursor.fetchall.return_value = [sample_drop_record]

        response = client.get("/api/search_drops", params={
            "query": 2000001,
            "query_type": "item"
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["itemid"] == 2000001
        mock_cursor.execute.assert_called_once()

    def test_search_drops_by_mob(self, client, mock_cursor, sample_drop_record):
        """Test searching drops by mob ID."""
        mock_cursor.fetchall.return_value = [sample_drop_record]

        response = client.get("/api/search_drops", params={
            "query": 100100,
            "query_type": "mob"
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_cursor.execute.assert_called_once()

    def test_search_drops_no_results(self, client, mock_cursor):
        """Test searching drops with no results."""
        mock_cursor.fetchall.return_value = []

        response = client.get("/api/search_drops", params={
            "query": 999999,
            "query_type": "item"
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_search_drops_missing_query(self, client):
        """Test searching drops without query parameter."""
        response = client.get("/api/search_drops", params={
            "query_type": "item"
        })

        assert response.status_code == 422

    def test_search_drops_missing_query_type(self, client):
        """Test searching drops without query_type parameter."""
        response = client.get("/api/search_drops", params={
            "query": 2000001
        })

        assert response.status_code == 422

    def test_search_drops_invalid_query_type(self, client):
        """Test searching drops with invalid query_type."""
        response = client.get("/api/search_drops", params={
            "query": 2000001,
            "query_type": "invalid"
        })

        assert response.status_code == 422

    def test_search_drops_id_converted_to_string(self, client, mock_cursor):
        """Test that record id is converted to string in response."""
        mock_cursor.fetchall.return_value = [{"id": 123, "itemid": 2000001}]

        response = client.get("/api/search_drops", params={
            "query": 2000001,
            "query_type": "item"
        })

        assert response.status_code == 200
        data = response.json()
        assert data[0]["id"] == "123"


class TestGetDrop:
    """Tests for /get_drop/{id} endpoint."""

    def test_get_drop_success(self, client, mock_cursor, sample_drop_record):
        """Test getting a drop by ID successfully."""
        mock_cursor.fetchone.return_value = sample_drop_record

        response = client.get("/get_drop/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"
        assert data["dropperid"] == 100100

    def test_get_drop_not_found(self, client, mock_cursor):
        """Test getting a drop that doesn't exist."""
        mock_cursor.fetchone.return_value = None

        response = client.get("/get_drop/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Drop record not found"

    def test_get_drop_invalid_id(self, client):
        """Test getting a drop with invalid ID format."""
        response = client.get("/get_drop/invalid")

        assert response.status_code == 422


class TestUpdateDrop:
    """Tests for /update_drop/{id} endpoint."""

    def test_update_drop_success(self, client, mock_writer_cursor, sample_drop_data):
        """Test updating a drop successfully."""
        response = client.put("/update_drop/1", json=sample_drop_data)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Drop data updated successfully"
        assert data["id"] == 1
        mock_writer_cursor.execute.assert_called_once()

    def test_update_drop_missing_field(self, client):
        """Test updating a drop with missing required field."""
        incomplete_data = {
            "dropperid": 100100,
            "itemid": 2000001
            # missing other required fields
        }

        response = client.put("/update_drop/1", json=incomplete_data)

        assert response.status_code == 422

    def test_update_drop_invalid_id(self, client, sample_drop_data):
        """Test updating a drop with invalid ID format."""
        response = client.put("/update_drop/invalid", json=sample_drop_data)

        assert response.status_code == 422


class TestAddDrop:
    """Tests for /add_drop endpoint."""

    def test_add_drop_success(self, client, mock_writer_cursor, sample_drop_data):
        """Test adding a drop successfully."""
        mock_writer_cursor.lastrowid = 42

        response = client.post("/add_drop", json=sample_drop_data)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Drop data added successfully"
        assert data["id"] == 42
        mock_writer_cursor.execute.assert_called_once()

    def test_add_drop_missing_field(self, client):
        """Test adding a drop with missing required field."""
        incomplete_data = {
            "dropperid": 100100,
            "itemid": 2000001
        }

        response = client.post("/add_drop", json=incomplete_data)

        assert response.status_code == 422

    def test_add_drop_invalid_data_type(self, client):
        """Test adding a drop with invalid data type."""
        invalid_data = {
            "dropperid": "not_an_int",
            "itemid": 2000001,
            "minimum_quantity": 1,
            "maximum_quantity": 5,
            "questid": 0,
            "chance": 100000
        }

        response = client.post("/add_drop", json=invalid_data)

        assert response.status_code == 422


class TestDeleteDrop:
    """Tests for /delete_drop/{id} endpoint."""

    def test_delete_drop_success(self, client, mock_writer_cursor):
        """Test deleting a drop successfully."""
        mock_writer_cursor.rowcount = 1

        response = client.delete("/delete_drop/1")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Drop data deleted successfully"
        assert data["id"] == 1

    def test_delete_drop_not_found(self, client, mock_writer_cursor):
        """Test deleting a drop that doesn't exist."""
        mock_writer_cursor.rowcount = 0

        response = client.delete("/delete_drop/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Drop record not found"

    def test_delete_drop_invalid_id(self, client):
        """Test deleting a drop with invalid ID format."""
        response = client.delete("/delete_drop/invalid")

        assert response.status_code == 422


class TestCheckDropsExist:
    """Tests for /api/drops/exist endpoint."""

    def test_check_drops_exist_success(self, client, mock_cursor):
        """Test checking drops existence successfully."""
        mock_cursor.fetchall.return_value = [
            {"type": "mob", "id": 100100}
        ]

        request_data = {
            "items": [
                {"type": "mob", "id": 100100},
                {"type": "item", "id": 2000001}
            ]
        }

        response = client.post("/api/drops/exist", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2

    def test_check_drops_exist_empty_list(self, client, mock_cursor):
        """Test checking drops existence with empty list."""
        request_data = {"items": []}

        response = client.post("/api/drops/exist", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []

    def test_check_drops_exist_invalid_type(self, client):
        """Test checking drops existence with invalid type."""
        request_data = {
            "items": [
                {"type": "invalid", "id": 100100}
            ]
        }

        response = client.post("/api/drops/exist", json=request_data)

        assert response.status_code == 422

    def test_check_drops_exist_all_exist(self, client, mock_cursor):
        """Test when all checked drops exist."""
        mock_cursor.fetchall.return_value = [
            {"type": "mob", "id": 100100},
            {"type": "item", "id": 2000001}
        ]

        request_data = {
            "items": [
                {"type": "mob", "id": 100100},
                {"type": "item", "id": 2000001}
            ]
        }

        response = client.post("/api/drops/exist", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert all(result["drop_exist"] for result in data["results"])

    def test_check_drops_exist_none_exist(self, client, mock_cursor):
        """Test when none of the checked drops exist."""
        mock_cursor.fetchall.return_value = []

        request_data = {
            "items": [
                {"type": "mob", "id": 999999},
                {"type": "item", "id": 888888}
            ]
        }

        response = client.post("/api/drops/exist", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert not any(result["drop_exist"] for result in data["results"])
