class ShipSyncError(Exception):
    pass


class TransportError(ShipSyncError):
    """The request did not produce a response."""


class ConnectionFailed(TransportError):
    pass


class RequestTimeout(TransportError):
    pass


class ApiError(ShipSyncError):
    """The carrier answered with a status of 400 or above."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


class LabelNotReady(ShipSyncError):
    def __init__(self, shipment_id: str) -> None:
        super().__init__(f"label for {shipment_id} is not ready")
        self.shipment_id = shipment_id
