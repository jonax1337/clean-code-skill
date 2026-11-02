I added `format_invoice_total`, which composes the existing `invoice_total` and `format_currency`, so it reuses the current rounding and German number formatting.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items) -> str:
+    return format_currency(invoice_total(items))
```

- **Output:** it returns the gross total (net + 19% VAT) as a string like `1.234,50 EUR`.
- **Rounding:** `format_currency` rounds half-up to two decimals, and `invoice_total` stays unrounded, so rounding happens once, at display time.
- **Currency:** it uses `format_currency`'s default of `"EUR"`. I didn't add a currency parameter since nothing needs it yet.

I couldn't run anything here, so this is untested. A focused test could look like this (assuming an item with `price` and `qty` attributes):

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import format_invoice_total


def test_format_invoice_total_returns_gross_total_as_display_string():
    items = [SimpleNamespace(price=Decimal("1000.00"), qty=1)]
    # 1000.00 net + 19% VAT = 1190.00
    assert format_invoice_total(items) == "1.190,00 EUR"
```