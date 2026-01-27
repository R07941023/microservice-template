import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from minio.error import S3Error


class TestGetImage:
    """Tests for /images/{type}/{dropper_id} endpoint."""

    def test_get_image_success(self, client, mock_minio_client, sample_image_data):
        """Test successfully retrieves image from MinIO."""
        mock_response = MagicMock()
        mock_response.read.return_value = sample_image_data
        mock_minio_client.get_object.return_value = mock_response

        response = client.get("/images/mob/100100")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content == sample_image_data
        mock_minio_client.get_object.assert_called_once()

    def test_get_image_item_type(self, client, mock_minio_client, sample_image_data):
        """Test successfully retrieves item image."""
        mock_response = MagicMock()
        mock_response.read.return_value = sample_image_data
        mock_minio_client.get_object.return_value = mock_response

        response = client.get("/images/item/2000001")

        assert response.status_code == 200

    def test_get_image_not_found(self, client, mock_minio_client):
        """Test returns 404 when image not found."""
        mock_minio_client.get_object.side_effect = Exception("NoSuchKey")

        response = client.get("/images/mob/999999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Image not found"

    def test_get_image_minio_error(self, client, mock_minio_client):
        """Test handles MinIO errors."""
        mock_minio_client.get_object.side_effect = Exception("Connection error")

        response = client.get("/images/mob/100100")

        assert response.status_code == 404


class TestCheckImagesExist:
    """Tests for /api/images/exist endpoint."""

    def test_check_images_exist_all_exist(self, client, mock_minio_client):
        """Test checking multiple images that all exist."""
        mock_minio_client.stat_object.return_value = MagicMock()

        request_data = {
            "images": [
                {"type": "mob", "id": 100100},
                {"type": "item", "id": 2000001}
            ]
        }

        with patch("main.check_single_image", new_callable=AsyncMock) as mock_check:
            from models import ImageExistence
            mock_check.side_effect = [
                ImageExistence(type="mob", id=100100, image_exist=True),
                ImageExistence(type="item", id=2000001, image_exist=True)
            ]

            response = client.post("/api/images/exist", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2
            assert all(r["image_exist"] for r in data["results"])

    def test_check_images_exist_none_exist(self, client, mock_minio_client):
        """Test checking multiple images that don't exist."""
        request_data = {
            "images": [
                {"type": "mob", "id": 999999},
                {"type": "item", "id": 888888}
            ]
        }

        with patch("main.check_single_image", new_callable=AsyncMock) as mock_check:
            from models import ImageExistence
            mock_check.side_effect = [
                ImageExistence(type="mob", id=999999, image_exist=False),
                ImageExistence(type="item", id=888888, image_exist=False)
            ]

            response = client.post("/api/images/exist", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2
            assert not any(r["image_exist"] for r in data["results"])

    def test_check_images_exist_mixed(self, client, mock_minio_client):
        """Test checking images with mixed existence."""
        request_data = {
            "images": [
                {"type": "mob", "id": 100100},
                {"type": "item", "id": 999999}
            ]
        }

        with patch("main.check_single_image", new_callable=AsyncMock) as mock_check:
            from models import ImageExistence
            mock_check.side_effect = [
                ImageExistence(type="mob", id=100100, image_exist=True),
                ImageExistence(type="item", id=999999, image_exist=False)
            ]

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
