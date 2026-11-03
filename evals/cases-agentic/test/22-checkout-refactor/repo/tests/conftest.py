import pytest

from shop.coupons import CouponBook
from shop.errors import PaymentDeclined
from shop.inventory import Inventory


class FakeGateway:
    def __init__(self, decline: bool = False) -> None:
        self.decline = decline
        self.charges: list[tuple[str, int]] = []
        self.refunds: list[tuple[str, int]] = []

    def charge(self, email: str, amount_cents: int) -> str:
        if self.decline:
            raise PaymentDeclined("card declined")
        self.charges.append((email, amount_cents))
        return f"rcpt-{len(self.charges)}"

    def refund(self, email: str, amount_cents: int) -> None:
        self.refunds.append((email, amount_cents))


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, int, str]] = []

    def send_receipt(self, email: str, order_id: int, receipt_id: str) -> None:
        self.sent.append((email, order_id, receipt_id))


@pytest.fixture
def inventory() -> Inventory:
    return Inventory({"pen": 10, "ink": 3})


@pytest.fixture
def gateway() -> FakeGateway:
    return FakeGateway()


@pytest.fixture
def notifier() -> FakeNotifier:
    return FakeNotifier()


@pytest.fixture
def coupons() -> CouponBook:
    return CouponBook({"SPRING10": (10, 2)})
