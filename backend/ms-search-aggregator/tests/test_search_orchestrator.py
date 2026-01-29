import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_orchestrator import search_and_augment_drops, aggregate_existence_by_name


class TestSearchAndAugmentDrops:
    """Tests for search_and_augment_drops function."""

    @pytest.mark.asyncio
    async def test_search_and_augment_drops_success(self, sample_drops):
        """Test successful search and augment."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            with patch("services.search_orchestrator.drop_repo_client") as mock_drop_repo:
                mock_name_resolver.resolve_name_to_id = AsyncMock(return_value={"id": 100100, "type": "mob"})
                mock_drop_repo.fetch_drops_by_mob_id = AsyncMock(return_value=sample_drops)
                mock_name_resolver.resolve_ids_to_names = AsyncMock(side_effect=[
                    {"100100": "Snail"},
                    {"2000001": "Red Potion", "2000002": "Blue Potion"}
                ])

                result = await search_and_augment_drops(mock_client, "Snail")

                assert len(result) == 2
                assert result[0].dropper_name == "Snail"
                assert result[0].item_name == "Red Potion"

    @pytest.mark.asyncio
    async def test_search_and_augment_drops_no_id_found(self):
        """Test returns empty when name not found."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            mock_name_resolver.resolve_name_to_id = AsyncMock(return_value=None)

            result = await search_and_augment_drops(mock_client, "NonExistent")

            assert result == []

    @pytest.mark.asyncio
    async def test_search_and_augment_drops_no_drops(self):
        """Test returns empty when no drops found."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            with patch("services.search_orchestrator.drop_repo_client") as mock_drop_repo:
                mock_name_resolver.resolve_name_to_id = AsyncMock(return_value={"id": 100100, "type": "mob"})
                mock_drop_repo.fetch_drops_by_mob_id = AsyncMock(return_value=[])

                result = await search_and_augment_drops(mock_client, "Snail")

                assert result == []

    @pytest.mark.asyncio
    async def test_search_and_augment_drops_unknown_names(self, sample_drops):
        """Test handles unknown dropper/item names."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            with patch("services.search_orchestrator.drop_repo_client") as mock_drop_repo:
                mock_name_resolver.resolve_name_to_id = AsyncMock(return_value={"id": 100100, "type": "mob"})
                mock_drop_repo.fetch_drops_by_mob_id = AsyncMock(return_value=sample_drops)
                mock_name_resolver.resolve_ids_to_names = AsyncMock(side_effect=[{}, {}])

                result = await search_and_augment_drops(mock_client, "Snail")

                assert len(result) == 2
                assert result[0].dropper_name == "Unknown"
                assert result[0].item_name == "Unknown"


class TestAggregateExistenceByName:
    """Tests for aggregate_existence_by_name function."""

    @pytest.mark.asyncio
    async def test_aggregate_existence_success(self, sample_name_id_results):
        """Test successful existence aggregation."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            with patch("services.search_orchestrator.image_retriever_client") as mock_image:
                with patch("services.search_orchestrator.drop_repo_client") as mock_drop:
                    mock_name_resolver.get_ids_for_name = AsyncMock(return_value=sample_name_id_results)
                    mock_image.check_images_exist = AsyncMock(return_value=[
                        {"type": "mob", "id": 100100, "image_exist": True},
                        {"type": "item", "id": 2000001, "image_exist": True}
                    ])
                    mock_drop.check_drops_exist = AsyncMock(return_value=[
                        {"type": "mob", "id": 100100, "drop_exist": True},
                        {"type": "item", "id": 2000001, "drop_exist": False}
                    ])

                    result = await aggregate_existence_by_name(mock_client, "Snail")

                    assert len(result) == 2

    @pytest.mark.asyncio
    async def test_aggregate_existence_no_ids_found(self):
        """Test returns empty when no IDs found for name."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            mock_name_resolver.get_ids_for_name = AsyncMock(return_value=[])

            result = await aggregate_existence_by_name(mock_client, "NonExistent")

            assert result == []

    @pytest.mark.asyncio
    async def test_aggregate_existence_partial_results(self, sample_name_id_results):
        """Test handles partial results from services."""
        mock_client = AsyncMock()

        with patch("services.search_orchestrator.name_resolver_client") as mock_name_resolver:
            with patch("services.search_orchestrator.image_retriever_client") as mock_image:
                with patch("services.search_orchestrator.drop_repo_client") as mock_drop:
                    mock_name_resolver.get_ids_for_name = AsyncMock(return_value=sample_name_id_results)
                    mock_image.check_images_exist = AsyncMock(return_value=[
                        {"type": "mob", "id": 100100, "image_exist": True}
                    ])
                    mock_drop.check_drops_exist = AsyncMock(return_value=[
                        {"type": "item", "id": 2000001, "drop_exist": True}
                    ])

                    result = await aggregate_existence_by_name(mock_client, "Snail")

                    assert len(result) == 2
