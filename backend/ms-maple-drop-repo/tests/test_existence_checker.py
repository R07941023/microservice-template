import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.existence_checker import check_existence
from models import ExistenceInfo, ExistenceResult


class TestCheckExistence:
    """Tests for the check_existence function."""

    def test_empty_items_list(self):
        """Test with empty items list."""
        mock_cursor = MagicMock()

        result = check_existence(mock_cursor, [])

        assert result == []
        mock_cursor.execute.assert_not_called()

    def test_mob_exists(self):
        """Test checking mob existence when mob exists in database."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"type": "mob", "id": 100100}
        ]

        items = [ExistenceInfo(type="mob", id=100100)]
        result = check_existence(mock_cursor, items)

        assert len(result) == 1
        assert result[0].type == "mob"
        assert result[0].id == 100100
        assert result[0].drop_exist is True

    def test_mob_not_exists(self):
        """Test checking mob existence when mob does not exist."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        items = [ExistenceInfo(type="mob", id=100100)]
        result = check_existence(mock_cursor, items)

        assert len(result) == 1
        assert result[0].type == "mob"
        assert result[0].id == 100100
        assert result[0].drop_exist is False

    def test_item_exists(self):
        """Test checking item existence when item exists in database."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"type": "item", "id": 2000001}
        ]

        items = [ExistenceInfo(type="item", id=2000001)]
        result = check_existence(mock_cursor, items)

        assert len(result) == 1
        assert result[0].type == "item"
        assert result[0].id == 2000001
        assert result[0].drop_exist is True

    def test_item_not_exists(self):
        """Test checking item existence when item does not exist."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        items = [ExistenceInfo(type="item", id=2000001)]
        result = check_existence(mock_cursor, items)

        assert len(result) == 1
        assert result[0].type == "item"
        assert result[0].id == 2000001
        assert result[0].drop_exist is False

    def test_mixed_mobs_and_items(self):
        """Test checking both mobs and items together."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"type": "mob", "id": 100100},
            {"type": "item", "id": 2000001}
        ]

        items = [
            ExistenceInfo(type="mob", id=100100),
            ExistenceInfo(type="mob", id=100200),
            ExistenceInfo(type="item", id=2000001),
            ExistenceInfo(type="item", id=2000002)
        ]
        result = check_existence(mock_cursor, items)

        assert len(result) == 4

        # Check mob 100100 exists
        assert result[0].type == "mob"
        assert result[0].id == 100100
        assert result[0].drop_exist is True

        # Check mob 100200 does not exist
        assert result[1].type == "mob"
        assert result[1].id == 100200
        assert result[1].drop_exist is False

        # Check item 2000001 exists
        assert result[2].type == "item"
        assert result[2].id == 2000001
        assert result[2].drop_exist is True

        # Check item 2000002 does not exist
        assert result[3].type == "item"
        assert result[3].id == 2000002
        assert result[3].drop_exist is False

    def test_only_mobs(self):
        """Test checking only mobs."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"type": "mob", "id": 100100},
            {"type": "mob", "id": 100200}
        ]

        items = [
            ExistenceInfo(type="mob", id=100100),
            ExistenceInfo(type="mob", id=100200),
            ExistenceInfo(type="mob", id=100300)
        ]
        result = check_existence(mock_cursor, items)

        assert len(result) == 3
        assert result[0].drop_exist is True
        assert result[1].drop_exist is True
        assert result[2].drop_exist is False

    def test_only_items(self):
        """Test checking only items."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"type": "item", "id": 2000001}
        ]

        items = [
            ExistenceInfo(type="item", id=2000001),
            ExistenceInfo(type="item", id=2000002)
        ]
        result = check_existence(mock_cursor, items)

        assert len(result) == 2
        assert result[0].drop_exist is True
        assert result[1].drop_exist is False

    def test_sql_query_construction_mobs_only(self):
        """Test that SQL query is constructed correctly for mobs only."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        items = [
            ExistenceInfo(type="mob", id=100100),
            ExistenceInfo(type="mob", id=100200)
        ]
        check_existence(mock_cursor, items)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "dropperid IN" in query
        assert "itemid IN" not in query
        assert params == (100100, 100200)

    def test_sql_query_construction_items_only(self):
        """Test that SQL query is constructed correctly for items only."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        items = [
            ExistenceInfo(type="item", id=2000001),
            ExistenceInfo(type="item", id=2000002)
        ]
        check_existence(mock_cursor, items)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "itemid IN" in query
        assert "dropperid IN" not in query
        assert params == (2000001, 2000002)

    def test_sql_query_construction_mixed(self):
        """Test that SQL query uses UNION ALL for mixed types."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        items = [
            ExistenceInfo(type="mob", id=100100),
            ExistenceInfo(type="item", id=2000001)
        ]
        check_existence(mock_cursor, items)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "UNION ALL" in query
        assert "dropperid IN" in query
        assert "itemid IN" in query
        assert params == (100100, 2000001)

    def test_result_order_preserved(self):
        """Test that result order matches input order."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"type": "item", "id": 2000001},
            {"type": "mob", "id": 100100}
        ]

        items = [
            ExistenceInfo(type="mob", id=100100),
            ExistenceInfo(type="item", id=2000001),
            ExistenceInfo(type="mob", id=100200)
        ]
        result = check_existence(mock_cursor, items)

        assert len(result) == 3
        assert result[0].type == "mob"
        assert result[0].id == 100100
        assert result[1].type == "item"
        assert result[1].id == 2000001
        assert result[2].type == "mob"
        assert result[2].id == 100200
