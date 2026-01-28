import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from minio.error import S3Error


class TestGetImage:
    """Tests for /images/{type}/{dropper_id} endpoint."""

    def test_get_image_success(self, client, sample_image_data):
        """Test successfully retrieves image from MinIO."""
        with patch("services.minio_service.fetch_image", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = sample_image_data

            response = client.get("/images/mob/100100")

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            assert response.content == sample_image_data

    def test_get_image_item_type(self, client, sample_image_data):
        """Test successfully retrieves item image."""
        with patch("services.minio_service.fetch_image", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = sample_image_data

            response = client.get("/images/item/2000001")

            assert response.status_code == 200

    def test_get_image_not_found(self, client):
        """Test returns 404 when image not found."""
        with patch("services.minio_service.fetch_image", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = S3Error(
                code="NoSuchKey",
                message="Object not found",
                resource="mob/999999.png",
                request_id="test",
                host_id="test",
                response=MagicMock()
            )

            response = client.get("/images/mob/999999")

            assert response.status_code == 404
            assert response.json()["detail"] == "Image not found"

    def test_get_image_minio_error(self, client):
        """Test handles MinIO errors."""
        with patch("services.minio_service.fetch_image", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = S3Error(
                code="InternalError",
                message="Connection error",
                resource="mob/100100.png",
                request_id="test",
                host_id="test",
                response=MagicMock()
            )

            response = client.get("/images/mob/100100")

            assert response.status_code == 404


class TestCheckImagesExist:
    """Tests for /api/images/exist endpoint."""

    def test_check_images_exist_all_exist(self, client):
        """Test checking multiple images that all exist."""
        with patch("services.minio_service.check_object_exists", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True

            request_data = {
                "images": [
                    {"type": "mob", "id": 100100},
                    {"type": "item", "id": 2000001}
                ]
            }

            response = client.post("/api/images/exist", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2
            assert all(r["image_exist"] for r in data["results"])

    def test_check_images_exist_none_exist(self, client):
        """Test checking multiple images that don't exist."""
        with patch("services.minio_service.check_object_exists", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False

            request_data = {
                "images": [
                    {"type": "mob", "id": 999999},
                    {"type": "item", "id": 888888}
                ]
            }

            response = client.post("/api/images/exist", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2
            assert not any(r["image_exist"] for r in data["results"])

    def test_check_images_exist_mixed(self, client):
        """Test checking images with mixed existence."""
        with patch("services.minio_service.check_object_exists", new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = [True, False]

            request_data = {
                "images": [
                    {"type": "mob", "id": 100100},
                    {"type": "item", "id": 999999}
                ]
            }

            response = client.post("/api/images/exist", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2

    def test_check_images_exist_empty_list(self, client):
        """Test checking with empty list."""
        request_data = {"images": []}

        response = client.post("/api/images/exist", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
