from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AddressBase(BaseModel):
    """Address fields and their validation rules."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Name associated with the address, such as Home or Office",
    )

    street: str = Field(
        min_length=1,
        max_length=255,
        description="Street or address line",
    )

    city: str = Field(min_length=1, max_length=100, description="City name")

    state: str = Field(min_length=1, max_length=100, description="State or region")

    country: str = Field(min_length=1, max_length=100, description="Country name")

    postal_code: str = Field(
        min_length=1,
        max_length=20,
        description="Postal or ZIP code",
    )

    latitude: float = Field(
        ge=-90,
        le=90,
        description="Geographical latitude, from -90 to 90",
    )

    longitude: float = Field(
        ge=-180,
        le=180,
        description="Geographical longitude, from -180 to 180",
    )


class AddressCreate(AddressBase):
    """Schema for creating a new address."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Office",
                "street": "Civil Lines",
                "city": "Nagpur",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "440001",
                "latitude": 21.1458,
                "longitude": 79.0882,
            }
        },
    )


class AddressUpdate(BaseModel):
    """Schema for partially updating an address."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "city": "Nagpur",
                "latitude": 21.1458,
                "longitude": 79.0882,
            }
        },
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Name associated with the address, such as Home or Office",
    )
    street: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Street or address line",
    )
    city: str | None = Field(
        default=None, min_length=1, max_length=100, description="City name"
    )
    state: str | None = Field(
        default=None, min_length=1, max_length=100, description="State or region"
    )
    country: str | None = Field(
        default=None, min_length=1, max_length=100, description="Country name"
    )
    postal_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        description="Postal or ZIP code",
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="Geographical latitude, from -90 to 90",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="Geographical longitude, from -180 to 180",
    )

    @model_validator(mode="after")
    def validate_update_fields(self) -> Self:
        """Make sure at least one field is sent, and that none of them is null."""

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class AddressResponse(AddressBase):
    """Schema for returning address information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def assume_utc(cls, value: datetime) -> datetime:
        # SQLite does not keep the timezone, so the value comes back without
        # one. We always save UTC, so we add the UTC timezone back.
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class AddressListResponse(BaseModel):
    """Schema for paginated address responses."""

    items: list[AddressResponse]
    total: int
    skip: int
    limit: int


class NearbyAddressItem(AddressResponse):
    """Address information with calculated distance."""

    distance_km: float = Field(
        description="Distance from the search point in kilometres, rounded to two decimal places",
    )


class NearbySearchLocation(BaseModel):
    """Coordinates used for nearby address search."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class NearbyAddressResponse(BaseModel):
    """Response schema for geographical search."""

    search_location: NearbySearchLocation
    distance_km: float = Field(
        description="Requested radius in kilometres. The boundary is inclusive.",
    )
    total: int
    items: list[NearbyAddressItem]
