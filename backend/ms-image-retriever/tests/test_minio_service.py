"""Tests for minio_service module."""

import pytest
from unittest.mock import MagicMock, patch
from minio.error import S3Error


class TestFetchObject:
    """Tests for _fetch_object function."""

    def test_fetch_object_success(self):
        """Test successfully fetches object and closes response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"test data"

        with patch("services.minio_service.minio_client") as mock_client:
            mock_client.get_object.return_value = mock_response

            from services.minio_service import _fetch_object
            result = _fetch_object("test_bucket", "test_object.png")

            assert result == b"test data"
            mock_client.get_object.assert_called_once_with("test_bucket", "test_object.png")
            mock_response.close.assert_called_once()
            mock_response.release_conn.assert_called_once()

    def test_fetch_object_error_still_closes(self):
        """Test response is closed even when read fails."""
        mock_response = MagicMock()
        mock_response.read.side_effect = Exception("Read error")

        with patch("services.minio_service.minio_client") as mock_client:
            mock_client.get_object.return_value = mock_response

            from services.minio_service import _fetch_object

            with pytest.raises(Exception, match="Read error"):
                _fetch_object("test_bucket", "test_object.png")

            mock_response.close.assert_called_once()
            mock_response.release_conn.assert_called_once()


class TestCheckBucketExists:
    """Tests for _check_bucket_exists function."""

    def test_bucket_exists(self):
        """Test returns True when bucket exists."""
        with patch("services.minio_service.minio_client") as mock_client:
            mock_client.bucket_exists.return_value = True

            from services.minio_service import _check_bucket_exists
            result = _check_bucket_exists("test_bucket")

            assert result is True
            mock_client.bucket_exists.assert_called_once_with("test_bucket")

    def test_bucket_not_exists(self):
        """Test returns False when bucket does not exist."""
        with patch("services.minio_service.minio_client") as mock_client:
            mock_client.bucket_exists.return_value = False

            from services.minio_service import _check_bucket_exists
            result = _check_bucket_exists("nonexistent_bucket")

            assert result is False


class TestCheckObjectExists:
    """Tests for _check_object_exists function."""

    def test_object_exists(self):
        """Test returns True when object exists."""
        with patch("services.minio_service.minio_client") as mock_client:
            mock_client.stat_object.return_value = MagicMock()

            from services.minio_service import _check_object_exists
            result = _check_object_exists("test_bucket", "test_object.png")

            assert result is True
            mock_client.stat_object.assert_called_once_with("test_bucket", "test_object.png")

    def test_object_not_exists(self):
        """Test returns False when object does not exist."""
        with patch("services.minio_service.minio_client") as mock_client:
            mock_client.stat_object.side_effect = S3Error(
                code="NoSuchKey",
                message="Object not found",
                resource="test_object.png",
                request_id="test",
                host_id="test",
                response=MagicMock()
            )

            from services.minio_service import _check_object_exists
            result = _check_object_exists("test_bucket", "test_object.png")

            assert result is False


class TestAsyncFunctions:
    """Tests for async wrapper functions."""

    @pytest.mark.asyncio
    async def test_fetch_image(self):
        """Test async fetch_image calls sync function via executor."""
        from concurrent.futures import ThreadPoolExecutor

        with patch("services.minio_service.executor", ThreadPoolExecutor(max_workers=1)):
            with patch("services.minio_service._fetch_object") as mock_fetch:
                mock_fetch.return_value = b"image data"

                from services.minio_service import fetch_image
                result = await fetch_image("test_bucket", "test.png")

                assert result == b"image data"

    @pytest.mark.asyncio
    async def test_check_bucket_exists_async(self):
        """Test async check_bucket_exists calls sync function via executor."""
        from concurrent.futures import ThreadPoolExecutor

        with patch("services.minio_service.executor", ThreadPoolExecutor(max_workers=1)):
            with patch("services.minio_service._check_bucket_exists") as mock_check:
                mock_check.return_value = True

                from services.minio_service import check_bucket_exists
                result = await check_bucket_exists("test_bucket")

                assert result is True

    @pytest.mark.asyncio
    async def test_check_object_exists_async(self):
        """Test async check_object_exists calls sync function via executor."""
        from concurrent.futures import ThreadPoolExecutor

        with patch("services.minio_service.executor", ThreadPoolExecutor(max_workers=1)):
            with patch("services.minio_service._check_object_exists") as mock_check:
                mock_check.return_value = True

                from services.minio_service import check_object_exists
                result = await check_object_exists("test_bucket", "test.png")

                assert result is True


class TestShutdown:
    """Tests for shutdown function."""

    def test_shutdown(self):
        """Test shutdown closes executor."""
        with patch("services.minio_service.executor") as mock_executor:
            from services.minio_service import shutdown
            shutdown()

            mock_executor.shutdown.assert_called_once_with(wait=True)
