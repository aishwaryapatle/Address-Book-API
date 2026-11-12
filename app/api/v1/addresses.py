from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.address import Address
from app.schemas.address import (
    AddressCreate,
    AddressListResponse,
    AddressResponse,
    AddressUpdate,
    NearbyAddressItem,
    NearbyAddressResponse,
    NearbySearchLocation,
)
from app.services import address_service


router = APIRouter(prefix="/addresses", tags=["Addresses"])

NOT_FOUND = {404: {"description": "Address not found"}}


def _to_nearby_item(address: Address, distance: float) -> NearbyAddressItem:
    """Combine an address with its distance (rounded to 2 decimals)."""
    base = AddressResponse.model_validate(address)
    return NearbyAddressItem(**base.model_dump(), distance_km=round(distance, 2))


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
):
    """Save a new address."""
    return address_service.create_address(db, address_data)


@router.get(
    "",
    response_model=AddressListResponse,
    summary="Retrieve all addresses",
)
def list_addresses(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return addresses in ID order. Use `skip` and `limit` to move through pages."""
    addresses, total = address_service.get_addresses(db, skip=skip, limit=limit)

    return AddressListResponse(
        items=addresses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/nearby",
    response_model=NearbyAddressResponse,
    summary="Find nearby addresses",
)
def find_nearby_addresses(
    latitude: float = Query(ge=-90, le=90, examples=[21.1458]),
    longitude: float = Query(ge=-180, le=180, examples=[79.0882]),
    distance_km: float = Query(
        gt=0,
        description="Search radius in kilometres (boundary is inclusive)",
        examples=[5],
    ),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return addresses within `distance_km` of the given point, nearest first."""
    results = address_service.get_nearby_addresses(
        db, latitude, longitude, distance_km
    )

    items = [_to_nearby_item(address, dist) for address, dist in results[:limit]]

    return NearbyAddressResponse(
        search_location=NearbySearchLocation(
            latitude=latitude,
            longitude=longitude,
        ),
        distance_km=distance_km,
        total=len(results),
        items=items,
    )


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Retrieve an address by ID",
    responses=NOT_FOUND,
)
def get_address(
    address_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    """Return one address. Responds with 404 if it does not exist."""
    return address_service.get_address_by_id(db, address_id)


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Replace an address",
    description="Full update. Every address field must be sent.",
    responses=NOT_FOUND,
)
def replace_address(
    address_data: AddressCreate,
    address_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    """Replace all fields of an existing address."""
    return address_service.update_address(db, address_id, address_data)


@router.patch(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Update part of an address",
    description="Partial update. Send at least one field. Null values are not allowed.",
    responses=NOT_FOUND,
)
def update_address(
    address_data: AddressUpdate,
    address_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    """Change only the fields sent in the request body."""
    return address_service.update_address(db, address_id, address_data)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an address",
    responses=NOT_FOUND,
)
def delete_address(
    address_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    """Delete an address. Responds with 404 if it does not exist."""
    address_service.delete_address(db, address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
