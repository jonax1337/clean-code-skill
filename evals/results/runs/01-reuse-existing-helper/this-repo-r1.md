I added `format_invoice_total`, which reuses the existing `invoice_total` and `format_currency`, so no calculation or formatting logic is duplicated.

```python
def format_invoice_total(items, currency: str = "EUR") -> str:
    return format_currency(invoice_total(items), currency)
```

It goes at the end of `billing/invoice.py`, after `invoice_total`. Nothing else in the file changes.

I haven't seen your test layout, so here is a test to adapt to it:

```python
from collections import namedtuple
from decimal import Decimal

from billing.invoice import format_invoice_total

Item = namedtuple("Item", "price qty")


def test_format_invoice_total_uses_german_separators_and_includes_vat():
    items = [Item(Decimal("1000.00"), 1)]

    assert format_invoice_total(items) == "1.190,00 EUR"


def test_format_invoice_total_rounds_gross_amount_half_up():
    items = [Item(Decimal("0.05"), 1)]  # gross 0.0595

    assert format_invoice_total(items) == "0,06 EUR"
```

- **Not run:** I couldn't run tools in this session, so neither the function nor the tests have been executed. I worked out the expected strings by hand, so please run them.
- **Rounding:** `invoice_total` returns an unrounded `Decimal` (net + VAT on the unrounded net), and rounding happens only in `format_currency`. The footer therefore shows the correctly rounded gross amount. If the invoice's line-level VAT must be rounded before summing, that is a separate question for `calc_vat`, and I left it alone.
- **Parameter:** I kept the `currency` parameter to match `format_currency`'s signature, defaulting to `"EUR"`. If the footer will only ever be EUR, it could be dropped.