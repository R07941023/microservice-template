import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import httpx


class TestSearchWithCache:
    """Tests for /search/{name} endpoint."""

    def test_search_cache_hit(self, client, mock_redis_client, sample_search_result):
        """Test search returns cached result when available."""
        mock_redis_client.get.return_value = json.dumps(sample_search_result)

        response = client.get("/search/snail")

        assert response.status_code == 200
        data = response.json()
        assert data == sample_search_result
        mock_redis_client.get.assert_called_once_with("search:snail")

    def test_search_cache_miss_fetches_from_aggregator(self, client, mock_redis_client, sample_search_result):
        """Test search fetches from aggregator on cache miss."""
        mock_redis_client.get.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = sample_search_result
        mock_response.text = json.dumps(sample_search_result)
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            response = client.get("/search/snail")

            assert response.status_code == 200
            mock_redis_client.setex.assert_called_once()

    def test_search_with_authorization_header(self, client, mock_redis_client, valid_jwt_token, sample_search_result):
        """Test search with Authorization header."""
        mock_redis_client.get.return_value = json.dumps(sample_search_result)

        response = client.get("/search/snail", headers={"Authorization": valid_jwt_token})

        assert response.status_code == 200

    def test_search_without_redis_client(self, client, sample_search_result):
        """Test search still works when Redis is unavailable."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_search_result
        mock_response.text = json.dumps(sample_search_result)
        mock_response.raise_for_status = MagicMock()

        with patch("main.redis_client", None):
            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = mock_response

                response = client.get("/search/snail")

                assert response.status_code == 200

    def test_search_aggregator_error(self, client, mock_redis_client):
        """Test search handles aggregator errors."""
        mock_redis_client.get.return_value = None

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection failed")

            response = client.get("/search/snail")

            assert response.status_code == 500
            assert "Error connecting to search aggregator" in response.json()["detail"]


class TestHealthCheck:
    """Tests for /health endpoint."""

    def test_health_check_success(self, client, mock_redis_client):
        """Test health check returns ok when Redis is connected."""
        mock_redis_client.ping.return_value = True

        with patch("main.redis_client", mock_redis_client):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["redis"] == "connected"

    def test_health_check_redis_disconnected(self, client):
        """Test health check fails when Redis is not connected."""
        with patch("main.redis_client", None):
            response = client.get("/health")

            assert response.status_code == 500
            assert "Redis client is not connected" in response.json()["detail"]

    def test_health_check_redis_error(self, client, mock_redis_client):
        """Test health check fails when Redis ping fails."""
        mock_redis_client.ping.side_effect = Exception("Connection error")

        with patch("main.redis_client", mock_redis_client):
            response = client.get("/health")

            assert response.status_code == 500
