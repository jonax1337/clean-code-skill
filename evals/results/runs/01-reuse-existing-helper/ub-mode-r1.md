I wrote the test first, but I can't run anything in this session, so I haven't seen it fail or pass. Run it before and after the change.

**1. Failing test** (`tests/test_invoice.py`, assuming that path suits your layout)

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import invoice_total_display


def item(price, qty):
    return SimpleNamespace(price=Decimal(price), qty=qty)


def test_gross_total_is_formatted_for_the_footer():
    items = [item("500.00", 1), item("250.00", 2)]  # net 1000.00, gross 1190.00
    assert invoice_total_display(items) == "1.190,00 EUR"


def test_gross_total_is_rounded_half_up_to_cents():
    items = [item("10.05", 1)]  # gross 11.9595
    assert invoice_total_display(items) == "11,96 EUR"
```

It should currently fail with an `ImportError`, because `invoice_total_display` doesn't exist yet.

**2. The change** (`billing/invoice.py`, append at the end)

```python
def invoice_total_display(items, currency: str = "EUR") -> str:
    return format_currency(invoice_total(items), currency)
```

**Why this shape**
- It reuses `invoice_total` for the amount and `format_currency` for the German formatting, so each rule still lives in one place.
- Rounding happens only once, in `format_currency`, after net and VAT are summed. That avoids rounding errors from rounding each part separately.
- `currency` defaults to `"EUR"` and is passed straight through, so it matches `format_currency`'s signature.

**Log**
1. I wrote two behavior tests that call the public function the way the PDF footer will. They cover thousands separators and half-up rounding.
2. I added a one-line composition of the existing functions, which is the smallest edit that solves the problem.
3. I did not run the CRAP, dryer, or mutator tools, and I did not commit or push. The tools aren't available here, and the directory isn't a git repo. When you commit, the message could be: "Add invoice_total_display for PDF footer; proved by two tests."