import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from minio.error import S3Error
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_checker import check_single_image
from models import ImageInfo, ImageExistence


class TestCheckSingleImage:
    """Tests for check_single_image function."""

    @pytest.mark.asyncio
    async def test_image_exists(self):
        """Test returns True when image exists."""
        mock_minio = MagicMock()
        mock_minio.stat_object.return_value = MagicMock()

        image_info = ImageInfo(type="mob", id=100100)

        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.return_value = MagicMock()

            result = await check_single_image(mock_minio, "test_bucket", image_info)

            assert result.type == "mob"
            assert result.id == 100100
            assert result.image_exist is True

    @pytest.mark.asyncio
    async def test_image_not_exists_no_such_key(self):
        """Test returns False when image doesn't exist (NoSuchKey)."""
        mock_minio = MagicMock()

        image_info = ImageInfo(type="mob", id=999999)

        s3_error = S3Error(
            code="NoSuchKey",
            message="Object not found",
            resource="mob/999999.png",
            request_id="test",
            host_id="test",
            response=MagicMock()
        )

        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.side_effect = s3_error

            result = await check_single_image(mock_minio, "test_bucket", image_info)

            assert result.type == "mob"
            assert result.id == 999999
            assert result.image_exist is False

    @pytest.mark.asyncio
    async def test_image_check_other_s3_error(self):
        """Test returns False on other S3 errors."""
        mock_minio = MagicMock()

        image_info = ImageInfo(type="item", id=2000001)

        s3_error = S3Error(
            code="AccessDenied",
            message="Access denied",
            resource="item/2000001.png",
            request_id="test",
            host_id="test",
            response=MagicMock()
        )

        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.side_effect = s3_error

            result = await check_single_image(mock_minio, "test_bucket", image_info)

            assert result.image_exist is False

    @pytest.mark.asyncio
    async def test_image_check_unexpected_error(self):
        """Test returns False on unexpected errors."""
        mock_minio = MagicMock()

        image_info = ImageInfo(type="mob", id=100100)

        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.side_effect = Exception("Unexpected error")

            result = await check_single_image(mock_minio, "test_bucket", image_info)

            assert result.image_exist is False


class TestImageModels:
    """Tests for image models."""

    def test_image_info_valid(self):
        """Test valid ImageInfo creation."""
        info = ImageInfo(type="mob", id=100100)
        assert info.type == "mob"
        assert info.id == 100100

    def test_image_existence_valid(self):
        """Test valid ImageExistence creation."""
        existence = ImageExistence(type="item", id=2000001, image_exist=True)
        assert existence.type == "item"
        assert existence.id == 2000001
        assert existence.image_exist is True
