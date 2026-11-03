I added `format_invoice_total`, which composes the two existing functions, so the VAT and rounding rules stay in one place.

**Test first** (`tests/test_invoice.py`, path assumed). I couldn't run it here, so I haven't seen it fail or pass.

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import format_invoice_total


def item(price, qty):
    return SimpleNamespace(price=Decimal(price), qty=qty)


def test_footer_total_is_gross_in_german_format():
    items = [item("100.00", 10)]
    assert format_invoice_total(items) == "1.190,00 EUR"


def test_footer_total_rounds_half_up_at_the_end():
    items = [item("10.01", 1)]  # 11.9119 gross
    assert format_invoice_total(items) == "11,91 EUR"
```

Before the change, both tests should fail with an `ImportError` because the function doesn't exist yet.

**Change** (`billing/invoice.py`, appended at the end):

```python
def format_invoice_total(items, currency: str = "EUR") -> str:
    return format_currency(invoice_total(items), currency)
```

**Why this shape**
- `invoice_total` already computes the gross amount, and `format_currency` already produces the `1.234,50 EUR` style. The new function only connects them.
- Rounding happens once, on the final gross amount. VAT isn't rounded separately, which matches how `invoice_total` works today.
- `currency` defaults to `"EUR"` like `format_currency`, so the footer call is just `format_invoice_total(items)`.

**Log**
1. Wrote two behavior tests against the public function, because the footer string is what the user sees.
2. Added a one-line composition instead of duplicating the VAT or formatting logic.
3. I didn't run the CRAP, dryer, or mutator tools, and I didn't commit or push, because I can't run tools or touch git in this session. The new function has no branches, so its complexity is minimal.