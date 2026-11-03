from dataclasses import dataclass, field
from decimal import Decimal

from shop.money import round_cents

VAT_RATES = {"standard": Decimal("0.19"), "reduced": Decimal("0.07")}


@dataclass(frozen=True)
class LineItem:
    sku: str
    name: str
    unit_price: Decimal  # net
    quantity: int
    vat_class: str = "standard"

    def net(self) -> Decimal:
        return self.unit_price * self.quantity

    def vat(self) -> Decimal:
        # Our tax advisor requires VAT to be rounded per line, not on the order total.
        return round_cents(self.net() * VAT_RATES[self.vat_class])


@dataclass
class Order:
    number: str
    customer_name: str
    customer_email: str
    items: list[LineItem] = field(default_factory=list)
    shipping: Decimal = Decimal("0")  # gross, no VAT split


def net_total(order: Order) -> Decimal:
    return sum((item.net() for item in order.items), Decimal("0"))


def vat_total(order: Order) -> Decimal:
    return sum((item.vat() for item in order.items), Decimal("0"))


def gross_total(order: Order) -> Decimal:
    return net_total(order) + vat_total(order) + order.shipping
