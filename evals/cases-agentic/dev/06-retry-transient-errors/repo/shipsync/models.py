from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Address:
    name: str
    street: str
    city: str
    postal_code: str
    country: str

    def to_payload(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Order:
    reference: str
    address: Address


@dataclass(frozen=True)
class Shipment:
    id: str
    order_ref: str
    status: str
    tracking_number: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Shipment":
        return cls(
            id=payload["id"],
            order_ref=payload["order_ref"],
            status=payload["status"],
            tracking_number=payload.get("tracking_number"),
        )
