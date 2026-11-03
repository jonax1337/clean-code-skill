from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    quantity: int
    unit_price_cents: int


@dataclass
class Customer:
    email: str
    country: str = "DE"
    vip: bool = False


@dataclass
class Order:
    id: int
    items: list[Item]
    coupon: str | None = None
    status: str = "new"
    total_cents: int = 0
