
import pytest
from pydantic import ValidationError

from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
)


@pytest.fixture
def valid_address_data():
    return {
        "name": "Home",
        "street": "MG Road",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "postal_code": "411001",
        "latitude": 18.5204,
        "longitude": 73.8567,
    }


def test_valid_address_creation(valid_address_data):
    address = AddressCreate(**valid_address_data)

    assert address.name == "Home"
    assert address.city == "Pune"
    assert address.latitude == 18.5204


@pytest.mark.parametrize(
    "latitude",
    [-91, 91, 100],
)
def test_invalid_latitude(valid_address_data, latitude):
    valid_address_data["latitude"] = latitude

    with pytest.raises(ValidationError):
        AddressCreate(**valid_address_data)


@pytest.mark.parametrize(
    "longitude",
    [-181, 181, 200],
)
def test_invalid_longitude(valid_address_data, longitude):
    valid_address_data["longitude"] = longitude

    with pytest.raises(ValidationError):
        AddressCreate(**valid_address_data)


def test_empty_name_is_invalid(valid_address_data):
    valid_address_data["name"] = ""

    with pytest.raises(ValidationError):
        AddressCreate(**valid_address_data)


def test_whitespace_only_name_is_invalid(valid_address_data):
    valid_address_data["name"] = "   "

    with pytest.raises(ValidationError):
        AddressCreate(**valid_address_data)


def test_partial_address_update():
    address = AddressUpdate(city="Mumbai")

    update_data = address.model_dump(exclude_unset=True)

    assert update_data == {"city": "Mumbai"}


def test_empty_address_update_is_invalid():
    with pytest.raises(ValidationError):
        AddressUpdate()


def test_null_update_value_is_invalid():
    with pytest.raises(ValidationError):
        AddressUpdate(city=None)
