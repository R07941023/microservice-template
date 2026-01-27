import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ResolveNamesRequest,
    ResolveNamesResponse,
    ResolveIdsRequest,
    ResolveIdsResponse,
    IdWithType,
    GetAllNamesResponse,
    NameIdType
)


class TestResolveNamesRequest:
    """Tests for ResolveNamesRequest model."""

    def test_valid_request(self):
        request = ResolveNamesRequest(idList=[100100, 100101], type="mob")
        assert request.idList == [100100, 100101]
        assert request.type == "mob"

    def test_empty_id_list(self):
        request = ResolveNamesRequest(idList=[], type="item")
        assert request.idList == []

    def test_missing_type(self):
        with pytest.raises(ValidationError):
            ResolveNamesRequest(idList=[100100])


class TestResolveNamesResponse:
    """Tests for ResolveNamesResponse model."""

    def test_valid_response(self):
        response = ResolveNamesResponse(names={"100100": "Snail", "100101": "Blue Snail"})
        assert response.names["100100"] == "Snail"

    def test_empty_names(self):
        response = ResolveNamesResponse(names={})
        assert response.names == {}


class TestResolveIdsRequest:
    """Tests for ResolveIdsRequest model."""

    def test_valid_request(self):
        request = ResolveIdsRequest(nameList=["Snail", "Blue Snail"])
        assert len(request.nameList) == 2

    def test_empty_name_list(self):
        request = ResolveIdsRequest(nameList=[])
        assert request.nameList == []


class TestIdWithType:
    """Tests for IdWithType model."""

    def test_valid_mob_type(self):
        id_type = IdWithType(id=100100, type="mob")
        assert id_type.id == 100100
        assert id_type.type == "mob"

    def test_valid_item_type(self):
        id_type = IdWithType(id=2000001, type="item")
        assert id_type.type == "item"

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            IdWithType(id=100100, type="invalid")


class TestResolveIdsResponse:
    """Tests for ResolveIdsResponse model."""

    def test_valid_response(self):
        response = ResolveIdsResponse(ids={
            "Snail": IdWithType(id=100100, type="mob")
        })
        assert response.ids["Snail"].id == 100100


class TestGetAllNamesResponse:
    """Tests for GetAllNamesResponse model."""

    def test_valid_response(self):
        response = GetAllNamesResponse(names=["Snail", "Blue Snail", "Red Potion"])
        assert len(response.names) == 3

    def test_empty_response(self):
        response = GetAllNamesResponse(names=[])
        assert response.names == []


class TestNameIdType:
    """Tests for NameIdType model."""

    def test_valid_model(self):
        model = NameIdType(type="mob", id=100100)
        assert model.type == "mob"
        assert model.id == 100100
