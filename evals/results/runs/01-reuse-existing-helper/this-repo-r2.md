Here is the change to `billing/invoice.py`. It reuses `invoice_total` and `format_currency`, so the rounding and the German number format stay in one place.

```python
def invoice_total_display(items) -> str:
    return format_currency(invoice_total(items))
```

I put it at the end of the file, after `invoice_total`.

Here is a test I'd add with it. I haven't seen your test layout, so adjust the location and imports:

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import invoice_total_display


def test_invoice_total_display_rounds_half_up_and_uses_german_format():
    # net 1037.50 + VAT 197.125 = 1234.625, which rounds half up to 1234.63
    items = [SimpleNamespace(price=Decimal("1037.50"), qty=1)]

    assert invoice_total_display(items) == "1.234,63 EUR"
```

- **Rounding:** the total is rounded only once, inside `format_currency`. `invoice_total` returns the unrounded gross, so the footer shows the same value you'd get by rounding the exact sum.
- **Currency:** the footer is always EUR, because `format_currency` defaults to it. I didn't add a currency parameter since nothing needs one yet.
- **Not run:** I couldn't run anything here, so the test and the expected string `1.234,63 EUR` are worked out by hand and not executed. Please run your test suite.