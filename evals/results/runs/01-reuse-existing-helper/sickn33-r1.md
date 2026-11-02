I added `format_invoice_total` at the end of `billing/invoice.py`. It reuses the existing `invoice_total` and `format_currency`, so the rounding and the German number format stay in one place.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    return format_currency(invoice_total(items), currency)
```

For example, items summing to a gross of `1234.50` return `"1.234,50 EUR"`.

- **Rounding:** `invoice_total` returns an unrounded `Decimal` (net × 1.19 can have more than two decimals). `format_currency` already quantizes with `ROUND_HALF_UP`, so the footer string is rounded correctly. No extra rounding is needed here.
- **Naming:** The `format_` prefix matches `format_currency` and says this returns a display string. `invoice_total` stays the numeric value.
- **Currency:** The optional `currency` argument passes straight through and defaults to `"EUR"`, as in `format_currency`.

I couldn't run anything in this session, so this is untested. A focused test would be:

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import format_invoice_total


def test_format_invoice_total_returns_german_formatted_gross():
    items = [SimpleNamespace(price=Decimal("1000.00"), qty=1)]  # net 1000.00 -> gross 1190.00
    assert format_invoice_total(items) == "1.190,00 EUR"
```

I left the older helpers (`calc_net`, `calc_vat`, and their short variable names) alone to keep this change scoped to what you asked. I can tidy those separately if you'd like.