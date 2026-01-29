import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import name_resolver_client, drop_repo_client, image_retriever_client


class TestNameResolverClient:
    """Tests for name_resolver_client functions."""

    @pytest.mark.asyncio
    async def test_resolve_name_to_id_success(self):
        """Test resolving name to ID."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"ids": {"Snail": {"id": 100100, "type": "mob"}}}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await name_resolver_client.resolve_name_to_id(mock_client, "Snail")

        assert result["id"] == 100100
        assert result["type"] == "mob"

    @pytest.mark.asyncio
    async def test_resolve_name_to_id_not_found(self):
        """Test resolving name that doesn't exist."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"ids": {}}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await name_resolver_client.resolve_name_to_id(mock_client, "NonExistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_ids_to_names_success(self):
        """Test resolving IDs to names."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"names": {"100100": "Snail", "100101": "Blue Snail"}}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await name_resolver_client.resolve_ids_to_names(mock_client, [100100, 100101], "mob")

        assert result["100100"] == "Snail"

    @pytest.mark.asyncio
    async def test_resolve_ids_to_names_empty_list(self):
        """Test resolving empty ID list."""
        mock_client = AsyncMock()

        result = await name_resolver_client.resolve_ids_to_names(mock_client, [], "mob")

        assert result == {}

    @pytest.mark.asyncio
    async def test_get_ids_for_name_success(self):
        """Test getting IDs for name."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [{"type": "mob", "id": 100100}]
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        result = await name_resolver_client.get_ids_for_name(mock_client, "Snail")

        assert len(result) == 1
        assert result[0]["id"] == 100100

    @pytest.mark.asyncio
    async def test_get_ids_for_name_empty(self):
        """Test getting IDs for empty name."""
        mock_client = AsyncMock()

        result = await name_resolver_client.get_ids_for_name(mock_client, "")

        assert result == []


class TestDropRepoClient:
    """Tests for drop_repo_client functions."""

    @pytest.mark.asyncio
    async def test_fetch_drops_by_mob_id_success(self):
        """Test fetching drops by mob ID."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "1", "dropperid": 100100, "itemid": 2000001}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        result = await drop_repo_client.fetch_drops_by_mob_id(
            mock_client,
            {"id": 100100, "type": "mob"}
        )

        assert len(result) == 1
        assert result[0]["dropperid"] == 100100

    @pytest.mark.asyncio
    async def test_check_drops_exist_success(self):
        """Test checking drops existence."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [
            {"type": "mob", "id": 100100, "drop_exist": True}
        ]}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await drop_repo_client.check_drops_exist(
            mock_client,
            [{"type": "mob", "id": 100100}]
        )

        assert len(result) == 1
        assert result[0]["drop_exist"] is True

    @pytest.mark.asyncio
    async def test_check_drops_exist_empty_list(self):
        """Test checking drops with empty list."""
        mock_client = AsyncMock()

        result = await drop_repo_client.check_drops_exist(mock_client, [])

        assert result == []


class TestImageRetrieverClient:
    """Tests for image_retriever_client functions."""

    @pytest.mark.asyncio
    async def test_check_images_exist_success(self):
        """Test checking images existence."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [
            {"type": "mob", "id": 100100, "image_exist": True}
        ]}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await image_retriever_client.check_images_exist(
            mock_client,
            [{"type": "mob", "id": 100100}]
        )

        assert len(result) == 1
        assert result[0]["image_exist"] is True

    @pytest.mark.asyncio
    async def test_check_images_exist_empty_list(self):
        """Test checking images with empty list."""
        mock_client = AsyncMock()

        result = await image_retriever_client.check_images_exist(mock_client, [])

        assert result == []
