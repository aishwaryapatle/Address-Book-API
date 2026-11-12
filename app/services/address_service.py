import logging
import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AddressNotFoundError
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate
from app.utils.geo import EARTH_RADIUS_KM, calculate_distance


logger = logging.getLogger(__name__)


def create_address(
    db: Session,
    address_data: AddressCreate,
) -> Address:
    """Save a new address."""

    address = Address(**address_data.model_dump())

    db.add(address)
    db.flush()

    logger.info("Created address with ID %s", address.id)

    return address


def get_addresses(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Address], int]:
    """Return one page of addresses and the total number of addresses."""

    total = db.scalar(select(func.count()).select_from(Address)) or 0

    statement = (
        select(Address)
        .order_by(Address.id)
        .offset(skip)
        .limit(limit)
    )

    addresses = list(db.scalars(statement).all())

    return addresses, total


def get_address_by_id(
    db: Session,
    address_id: int,
) -> Address:
    """Return the address with this ID. Raise an error if it is missing."""

    address = db.get(Address, address_id)

    if address is None:
        raise AddressNotFoundError(address_id)

    return address


def update_address(
    db: Session,
    address_id: int,
    address_data: AddressCreate | AddressUpdate,
) -> Address:
    """
    Update an existing address.

    Only the fields sent by the client are changed. A PUT sends every
    field, a PATCH sends only some of them.
    """

    address = get_address_by_id(db, address_id)

    update_data = address_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(address, field, value)

    db.flush()

    logger.info("Updated address with ID %s", address_id)

    return address


def delete_address(
    db: Session,
    address_id: int,
) -> None:
    """Delete the address with this ID. Raise an error if it is missing."""

    address = get_address_by_id(db, address_id)

    db.delete(address)
    db.flush()

    logger.info("Deleted address with ID %s", address_id)


def get_nearby_addresses(
    db: Session,
    latitude: float,
    longitude: float,
    distance_km: float,
) -> list[tuple[Address, float]]:
    """
    Find the addresses within distance_km of the given point.

    Returns a list of (address, distance_in_km), nearest first.
    If two distances are equal, the lower ID comes first.
    """

    # First, ask the database only for rows in a latitude band. A point that
    # is within distance_km cannot be outside this band, so nothing is missed.
    # The tiny extra margin protects points that sit exactly on the edge.
    lat_margin = math.degrees(distance_km / EARTH_RADIUS_KM) + 1e-6

    statement = select(Address).where(
        Address.latitude.between(latitude - lat_margin, latitude + lat_margin)
    )
    addresses = db.scalars(statement).all()

    nearby_results: list[tuple[Address, float]] = []

    for address in addresses:
        distance = calculate_distance(
            latitude,
            longitude,
            address.latitude,
            address.longitude,
        )

        if distance <= distance_km:
            nearby_results.append((address, distance))

    nearby_results.sort(key=lambda item: (item[1], item[0].id))

    return nearby_results
