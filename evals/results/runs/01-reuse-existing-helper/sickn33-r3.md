I added `format_gross_total`, which reuses `invoice_total` and `format_currency`, so the VAT and rounding rules stay in one place.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_gross_total(items, currency: str = "EUR") -> str:
+    return format_currency(invoice_total(items), currency)
```

For the PDF footer, call `format_gross_total(items)`. A gross total of `1234.5` renders as `1.234,50 EUR`.

- **Rounding:** `invoice_total` returns an unrounded `Decimal`. `format_currency` quantizes it with `ROUND_HALF_UP` only at display time, so rounding happens once, at the end.
- **Currency:** the `currency` parameter defaults to `"EUR"`, matching `format_currency`.
- **Scope:** I left the existing functions alone. `calc_net` has terse local names (`t`, `i`), which would be worth a separate cleanup, but I kept it out of this change.

I couldn't run anything here, so this is untested. Here's a focused test you can add:

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import format_gross_total


def test_format_gross_total_applies_vat_and_german_formatting():
    items = [SimpleNamespace(price=Decimal("500.00"), qty=2)]  # net 1000.00, VAT 190.00

    assert format_gross_total(items) == "1.190,00 EUR"
```