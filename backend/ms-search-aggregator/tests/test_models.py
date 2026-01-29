import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    AugmentedDrop,
    AugmentedSearchResponse,
    IdInfo,
    ExistenceInfo,
    ExistenceResponse
)


class TestAugmentedDrop:
    """Tests for AugmentedDrop model."""

    def test_valid_augmented_drop(self):
        drop = AugmentedDrop(
            id="1",
            dropperid=100100,
            dropper_name="Snail",
            itemid=2000001,
            item_name="Red Potion",
            minimum_quantity=1,
            maximum_quantity=5,
            questid=0,
            chance=100000
        )
        assert drop.dropperid == 100100
        assert drop.dropper_name == "Snail"
        assert drop.item_name == "Red Potion"

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            AugmentedDrop(
                id="1",
                dropperid=100100,
                # missing dropper_name
                itemid=2000001,
                item_name="Red Potion",
                minimum_quantity=1,
                maximum_quantity=5,
                questid=0,
                chance=100000
            )


class TestAugmentedSearchResponse:
    """Tests for AugmentedSearchResponse model."""

    def test_valid_response(self):
        response = AugmentedSearchResponse(data=[
            AugmentedDrop(
                id="1",
                dropperid=100100,
                dropper_name="Snail",
                itemid=2000001,
                item_name="Red Potion",
                minimum_quantity=1,
                maximum_quantity=1,
                questid=0,
                chance=100000
            )
        ])
        assert len(response.data) == 1

    def test_empty_response(self):
        response = AugmentedSearchResponse(data=[])
        assert response.data == []


class TestIdInfo:
    """Tests for IdInfo model."""

    def test_valid_mob_id_info(self):
        info = IdInfo(id=100100, type="mob")
        assert info.id == 100100
        assert info.type == "mob"

    def test_valid_item_id_info(self):
        info = IdInfo(id=2000001, type="item")
        assert info.type == "item"

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            IdInfo(id=100100, type="invalid")


class TestExistenceInfo:
    """Tests for ExistenceInfo model."""

    def test_valid_existence_info(self):
        info = ExistenceInfo(
            id=100100,
            type="mob",
            image_exist=True,
            drop_exist=False
        )
        assert info.id == 100100
        assert info.image_exist is True
        assert info.drop_exist is False


class TestExistenceResponse:
    """Tests for ExistenceResponse model."""

    def test_valid_response(self):
        response = ExistenceResponse(results=[
            ExistenceInfo(id=100100, type="mob", image_exist=True, drop_exist=True),
            ExistenceInfo(id=2000001, type="item", image_exist=False, drop_exist=True)
        ])
        assert len(response.results) == 2

    def test_empty_response(self):
        response = ExistenceResponse(results=[])
        assert response.results == []
