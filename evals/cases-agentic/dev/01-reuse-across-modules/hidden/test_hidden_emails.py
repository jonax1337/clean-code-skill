import re
from decimal import Decimal

from shop.emails import confirmation_body
from shop.orders import LineItem, Order

# 974.65 net + 176.21 VAT (rounded per line) + 4.90 shipping = 1,155.76.
# VAT rounded on the total gives 1,155.75; forgetting shipping gives 1,150.86.
EXPECTED_TOTAL_LINE = "Gesamtbetrag: 1.155,76 EUR"

ORDER = Order(
    number="A-2042",
    customer_name="Erika Mustermann",
    customer_email="erika@example.com",
    items=[
        LineItem("TV", "Fernseher", Decimal("899.00"), 1),
        LineItem("BK", "Kochbuch", Decimal("24.95"), 3, "reduced"),
        LineItem("CB", "Kabel", Decimal("0.05"), 7),
        LineItem("ST", "Sticker", Decimal("0.15"), 3),
    ],
    shipping=Decimal("4.90"),
)


def original_body(order: Order) -> str:
    """The email text before the change, for comparing everything except the new line."""
    items = "".join(f"  {item.quantity} x {item.name}\n" for item in order.items)
    return (
        f"Hallo {order.customer_name},\n\n"
        f"vielen Dank für Ihre Bestellung {order.number}.\n\n"
        f"Sie haben bestellt:\n{items}\n"
        "Wir melden uns, sobald Ihre Bestellung versandt wurde.\n\n"
        "Viele Grüße\nIhr Shop-Team\n"
    )


def collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def test_gross_total_follows_shop_rules_and_formatting():
    assert EXPECTED_TOTAL_LINE in confirmation_body(ORDER).split("\n")


def test_total_line_comes_right_after_the_item_list():
    lines = confirmation_body(ORDER).split("\n")
    total_at = lines.index(EXPECTED_TOTAL_LINE)
    closing_at = next(i for i, line in enumerate(lines) if line.startswith("Wir melden uns"))
    assert lines.index("  3 x Sticker") < total_at < closing_at


def test_rest_of_the_email_is_unchanged():
    lines = [line for line in confirmation_body(ORDER).split("\n") if line != EXPECTED_TOTAL_LINE]
    assert collapse_blank_lines("\n".join(lines)) == collapse_blank_lines(original_body(ORDER))
