import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    DropUpdate,
    DropCreate,
    ExistenceInfo,
    ExistenceCheckRequest,
    ExistenceResult,
    ExistenceCheckResponse
)


class TestDropUpdate:
    """Tests for DropUpdate model."""

    def test_valid_drop_update(self):
        drop = DropUpdate(
            dropperid=100100,
            itemid=2000001,
            minimum_quantity=1,
            maximum_quantity=5,
            questid=0,
            chance=100000
        )
        assert drop.dropperid == 100100
        assert drop.itemid == 2000001
        assert drop.minimum_quantity == 1
        assert drop.maximum_quantity == 5
        assert drop.questid == 0
        assert drop.chance == 100000

    def test_drop_update_missing_field(self):
        with pytest.raises(ValidationError):
            DropUpdate(
                dropperid=100100,
                itemid=2000001,
                minimum_quantity=1,
                maximum_quantity=5,
                questid=0
                # missing chance
            )

    def test_drop_update_invalid_type(self):
        with pytest.raises(ValidationError):
            DropUpdate(
                dropperid="not_an_int",
                itemid=2000001,
                minimum_quantity=1,
                maximum_quantity=5,
                questid=0,
                chance=100000
            )


class TestDropCreate:
    """Tests for DropCreate model."""

    def test_valid_drop_create(self):
        drop = DropCreate(
            dropperid=100100,
            itemid=2000001,
            minimum_quantity=1,
            maximum_quantity=5,
            questid=0,
            chance=100000
        )
        assert drop.dropperid == 100100
        assert drop.itemid == 2000001

    def test_drop_create_missing_field(self):
        with pytest.raises(ValidationError):
            DropCreate(
                dropperid=100100,
                itemid=2000001
                # missing other required fields
            )


class TestExistenceInfo:
    """Tests for ExistenceInfo model."""

    def test_valid_mob_existence_info(self):
        info = ExistenceInfo(type="mob", id=100100)
        assert info.type == "mob"
        assert info.id == 100100

    def test_valid_item_existence_info(self):
        info = ExistenceInfo(type="item", id=2000001)
        assert info.type == "item"
        assert info.id == 2000001

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            ExistenceInfo(type="invalid", id=100100)

    def test_invalid_id_type(self):
        with pytest.raises(ValidationError):
            ExistenceInfo(type="mob", id="not_an_int")


class TestExistenceCheckRequest:
    """Tests for ExistenceCheckRequest model."""

    def test_valid_request(self):
        request = ExistenceCheckRequest(items=[
            ExistenceInfo(type="mob", id=100100),
            ExistenceInfo(type="item", id=2000001)
        ])
        assert len(request.items) == 2
        assert request.items[0].type == "mob"
        assert request.items[1].type == "item"

    def test_empty_items_list(self):
        request = ExistenceCheckRequest(items=[])
        assert len(request.items) == 0


class TestExistenceResult:
    """Tests for ExistenceResult model."""

    def test_valid_result_exists(self):
        result = ExistenceResult(type="mob", id=100100, drop_exist=True)
        assert result.type == "mob"
        assert result.id == 100100
        assert result.drop_exist is True

    def test_valid_result_not_exists(self):
        result = ExistenceResult(type="item", id=2000001, drop_exist=False)
        assert result.type == "item"
        assert result.id == 2000001
        assert result.drop_exist is False


class TestExistenceCheckResponse:
    """Tests for ExistenceCheckResponse model."""

    def test_valid_response(self):
        response = ExistenceCheckResponse(results=[
            ExistenceResult(type="mob", id=100100, drop_exist=True),
            ExistenceResult(type="item", id=2000001, drop_exist=False)
        ])
        assert len(response.results) == 2
        assert response.results[0].drop_exist is True
        assert response.results[1].drop_exist is False

    def test_empty_response(self):
        response = ExistenceCheckResponse(results=[])
        assert len(response.results) == 0
