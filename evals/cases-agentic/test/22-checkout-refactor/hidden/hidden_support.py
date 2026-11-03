from shop.coupons import CouponBook
from shop.errors import PaymentDeclined
from shop.inventory import Inventory
from shop.models import Customer, Item, Order


class RecordingGateway:
    def __init__(self, inventory: Inventory | None = None, decline: bool = False, crash: bool = False) -> None:
        self.inventory = inventory
        self.decline = decline
        self.crash = crash
        self.charges: list[tuple[str, int]] = []
        self.inventory_log_at_charge: list[tuple[str, str, int]] = []

    def charge(self, email: str, amount_cents: int) -> str:
        if self.inventory is not None:
            self.inventory_log_at_charge = list(self.inventory.log)
        if self.crash:
            raise RuntimeError("gateway unreachable")
        if self.decline:
            raise PaymentDeclined("card declined")
        self.charges.append((email, amount_cents))
        return f"rcpt-{len(self.charges)}"

    def refund(self, email: str, amount_cents: int) -> None:
        raise AssertionError("checkout must not refund")


class RecordingNotifier:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, int, str]] = []

    def send_receipt(self, email: str, order_id: int, receipt_id: str) -> None:
        if self.fail:
            raise RuntimeError("smtp down")
        self.sent.append((email, order_id, receipt_id))


def make_inventory() -> Inventory:
    return Inventory({"pen": 50, "ink": 3, "pad": 20})


def make_coupons(uses: int = 2) -> CouponBook:
    return CouponBook({"SPRING10": (10, uses)})


def make_order(*items: Item, coupon: str | None = None) -> Order:
    return Order(id=7, items=list(items), coupon=coupon)


def customer(country: str = "DE", vip: bool = False) -> Customer:
    return Customer(email="ada@example.com", country=country, vip=vip)
