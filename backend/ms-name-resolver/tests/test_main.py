import pytest
from unittest.mock import patch, MagicMock


class TestResolveNames:
    """Tests for /api/id-names/resolve endpoint."""

    def test_resolve_names_success(self, client, mock_collection, sample_mob_docs):
        """Test resolving IDs to names."""
        mock_collection.find.return_value = iter(sample_mob_docs)

        request_data = {
            "idList": [100100, 100101],
            "type": "mob"
        }

        response = client.post("/api/id-names/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "100100" in data["names"]
        assert data["names"]["100100"] == "Snail"
        assert data["names"]["100101"] == "Blue Snail"

    def test_resolve_names_empty_list(self, client, mock_collection):
        """Test resolving empty ID list."""
        mock_collection.find.return_value = iter([])

        request_data = {
            "idList": [],
            "type": "mob"
        }

        response = client.post("/api/id-names/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["names"] == {}

    def test_resolve_names_not_found(self, client, mock_collection):
        """Test resolving IDs that don't exist."""
        mock_collection.find.return_value = iter([])

        request_data = {
            "idList": [999999],
            "type": "mob"
        }

        response = client.post("/api/id-names/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["names"] == {}

    def test_resolve_names_item_type(self, client, mock_collection, sample_item_docs):
        """Test resolving item IDs to names."""
        mock_collection.find.return_value = iter(sample_item_docs)

        request_data = {
            "idList": [2000001, 2000002],
            "type": "item"
        }

        response = client.post("/api/id-names/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["names"]["2000001"] == "Red Potion"


class TestResolveIds:
    """Tests for /api/names-id/resolve endpoint."""

    def test_resolve_ids_success(self, client, mock_collection, sample_mob_docs):
        """Test resolving names to IDs."""
        mock_collection.find.return_value = iter(sample_mob_docs)

        request_data = {
            "nameList": ["Snail", "Blue Snail"]
        }

        response = client.post("/api/names-id/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "Snail" in data["ids"]
        assert data["ids"]["Snail"]["id"] == 100100
        assert data["ids"]["Snail"]["type"] == "mob"

    def test_resolve_ids_empty_list(self, client, mock_collection):
        """Test resolving empty name list."""
        mock_collection.find.return_value = iter([])

        request_data = {
            "nameList": []
        }

        response = client.post("/api/names-id/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["ids"] == {}

    def test_resolve_ids_not_found(self, client, mock_collection):
        """Test resolving names that don't exist."""
        mock_collection.find.return_value = iter([])

        request_data = {
            "nameList": ["NonExistent"]
        }

        response = client.post("/api/names-id/resolve", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["ids"] == {}


class TestGetAllNames:
    """Tests for /api/names/all endpoint."""

    def test_get_all_names_success(self, client, mock_collection):
        """Test getting all unique names."""
        mock_collection.distinct.return_value = ["Snail", "Blue Snail", "Red Potion"]

        response = client.get("/api/names/all")

        assert response.status_code == 200
        data = response.json()
        assert len(data["names"]) == 3
        assert "Snail" in data["names"]

    def test_get_all_names_empty(self, client, mock_collection):
        """Test getting names when collection is empty."""
        mock_collection.distinct.return_value = []

        response = client.get("/api/names/all")

        assert response.status_code == 200
        data = response.json()
        assert data["names"] == []


class TestGetIdsByName:
    """Tests for /api/name-to-ids/{name} endpoint."""

    def test_get_ids_by_name_success(self, client, mock_collection):
        """Test getting IDs for a name."""
        mock_collection.find.return_value = iter([
            {"id": 100100, "type": "mob"},
            {"id": 2000001, "type": "item"}
        ])

        response = client.get("/api/name-to-ids/Snail")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_ids_by_name_not_found(self, client, mock_collection):
        """Test getting IDs for non-existent name."""
        mock_collection.find.return_value = iter([])

        response = client.get("/api/name-to-ids/NonExistent")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_ids_by_name_single_result(self, client, mock_collection):
        """Test getting single ID for a name."""
        mock_collection.find.return_value = iter([
            {"id": 100100, "type": "mob"}
        ])

        response = client.get("/api/name-to-ids/Snail")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 100100
        assert data[0]["type"] == "mob"
