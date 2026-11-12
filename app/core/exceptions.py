class AddressNotFoundError(Exception):
    """Raised when no address exists with the given ID."""

    def __init__(self, address_id: int) -> None:
        self.address_id = address_id
        super().__init__(f"Address with ID {address_id} not found")
