from decimal import Decimal

from shop.emails import confirmation_body, is_sendable, subject
from shop.orders import LineItem, Order


def make_order(**overrides):
    defaults = dict(
        number="A-1001",
        customer_name="Erika Mustermann",
        customer_email="erika@example.com",
        items=[LineItem("BK-1", "Clean Code", Decimal("30.00"), 1, "reduced")],
    )
    return Order(**{**defaults, **overrides})


def test_subject_contains_order_number():
    assert subject(make_order()) == "Ihre Bestellung A-1001 ist eingegangen"


def test_body_greets_customer_and_lists_items():
    body = confirmation_body(make_order())
    assert body.startswith("Hallo Erika Mustermann,\n")
    assert "  1 x Clean Code\n" in body


def test_order_without_email_is_not_sendable():
    assert not is_sendable(make_order(customer_email=""))
