import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx


class TestGetImage:
    """Tests for /images/{type}/{dropper_id} endpoint."""

    def test_get_image_cache_hit(self, client, mock_redis_client, sample_image_data):
        """Test returns cached image when available."""
        mock_redis_client.get.return_value = sample_image_data

        response = client.get("/images/mob/100100")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content == sample_image_data
        mock_redis_client.get.assert_called_once_with("image:mob:100100")

    def test_get_image_cache_miss_fetches_from_retriever(self, client, mock_redis_client, sample_image_data):
        """Test fetches from image retriever on cache miss."""
        mock_redis_client.get.return_value = None

        mock_response = MagicMock()
        mock_response.content = sample_image_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            response = client.get("/images/mob/100100")

            assert response.status_code == 200
            assert response.content == sample_image_data
            mock_redis_client.setex.assert_called_once()

    def test_get_image_item_type(self, client, mock_redis_client, sample_image_data):
        """Test fetching item type image."""
        mock_redis_client.get.return_value = sample_image_data

        response = client.get("/images/item/2000001")

        assert response.status_code == 200
        mock_redis_client.get.assert_called_once_with("image:item:2000001")

    def test_get_image_retriever_not_found(self, client, mock_redis_client):
        """Test handles 404 from image retriever."""
        mock_redis_client.get.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Image not found"

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found",
                request=MagicMock(),
                response=mock_response
            )

            response = client.get("/images/mob/999999")

            assert response.status_code == 404

    def test_get_image_retriever_connection_error(self, client, mock_redis_client):
        """Test handles connection error to image retriever."""
        mock_redis_client.get.return_value = None

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection failed")

            response = client.get("/images/mob/100100")

            assert response.status_code == 500
            assert "Could not connect to image retriever service" in response.json()["detail"]

    def test_get_image_without_redis(self, client, sample_image_data):
        """Test works when Redis is unavailable."""
        mock_response = MagicMock()
        mock_response.content = sample_image_data
        mock_response.raise_for_status = MagicMock()

        with patch("main.redis_client", None):
            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = mock_response

                response = client.get("/images/mob/100100")

                assert response.status_code == 200
                assert response.content == sample_image_data

    def test_get_image_redis_error_on_get(self, client, mock_redis_client, sample_image_data):
        """Test handles Redis get error gracefully."""
        mock_redis_client.get.side_effect = Exception("Redis error")

        mock_response = MagicMock()
        mock_response.content = sample_image_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            response = client.get("/images/mob/100100")

            assert response.status_code == 200

    def test_get_image_redis_error_on_set(self, client, mock_redis_client, sample_image_data):
        """Test handles Redis setex error gracefully."""
        mock_redis_client.get.return_value = None
        mock_redis_client.setex.side_effect = Exception("Redis error")

        mock_response = MagicMock()
        mock_response.content = sample_image_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            response = client.get("/images/mob/100100")

            # Should still return image even if caching fails
            assert response.status_code == 200
            assert response.content == sample_image_data
