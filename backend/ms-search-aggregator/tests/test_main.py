import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

# Mock authorization header for all tests
AUTH_HEADERS = {"Authorization": "Bearer mock-token"}


class TestSearchDropsAugmented:
    """Tests for /api/search/drops-augmented endpoint."""

    def test_search_drops_augmented_success(self, client, sample_augmented_drops):
        """Test successful augmented search."""
        with patch("main.search_and_augment_drops", new_callable=AsyncMock) as mock_search:
            from models import AugmentedDrop
            mock_search.return_value = [AugmentedDrop(**d) for d in sample_augmented_drops]

            response = client.get(
                "/api/search/drops-augmented",
                params={"name": "Snail"},
                headers=AUTH_HEADERS,
            )

            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert len(data["data"]) == 1

    def test_search_drops_augmented_empty_result(self, client):
        """Test search with no results."""
        with patch("main.search_and_augment_drops", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []

            response = client.get(
                "/api/search/drops-augmented",
                params={"name": "NonExistent"},
                headers=AUTH_HEADERS,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"] == []

    def test_search_drops_augmented_missing_name(self, client):
        """Test search without name parameter."""
        response = client.get("/api/search/drops-augmented", headers=AUTH_HEADERS)

        assert response.status_code == 422

    def test_search_drops_augmented_http_error(self, client):
        """Test search handles HTTP errors from downstream services."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("main.search_and_augment_drops", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=mock_response
            )

            response = client.get(
                "/api/search/drops-augmented",
                params={"name": "Snail"},
                headers=AUTH_HEADERS,
            )

            assert response.status_code == 500


class TestExistenceCheck:
    """Tests for /api/existence-check/{name} endpoint."""

    def test_existence_check_success(self, client):
        """Test successful existence check."""
        with patch("main.aggregate_existence_by_name", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = [
                {"type": "mob", "id": 100100, "image_exist": True, "drop_exist": True},
                {"type": "item", "id": 2000001, "image_exist": True, "drop_exist": False}
            ]

            response = client.get("/api/existence-check/Snail", headers=AUTH_HEADERS)

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 2

    def test_existence_check_empty_result(self, client):
        """Test existence check with no results."""
        with patch("main.aggregate_existence_by_name", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = []

            response = client.get("/api/existence-check/NonExistent", headers=AUTH_HEADERS)

            assert response.status_code == 200
            data = response.json()
            assert data["results"] == []

    def test_existence_check_http_error(self, client):
        """Test existence check handles HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("main.aggregate_existence_by_name", new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=mock_response
            )

            response = client.get("/api/existence-check/Snail", headers=AUTH_HEADERS)

            assert response.status_code == 404
