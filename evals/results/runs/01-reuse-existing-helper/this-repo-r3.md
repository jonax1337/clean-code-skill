I added `format_invoice_total`, which reuses `invoice_total` and `format_currency` so the rounding and the `1.234,50 EUR` formatting stay in one place.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items) -> str:
+    return format_currency(invoice_total(items))
```

`invoice_total` is not rounded, so the rounding happens once, in `format_currency`, with `ROUND_HALF_UP`. I did not add a `currency` parameter because nothing needs it yet. `format_currency` already defaults to `EUR`, and the function can pass a currency through when a second one appears.

I haven't run anything, and I can't see your test setup. If you have tests, this one pins the behavior, including a half-up rounding case (100.50 × 1.19 = 119.595, which becomes 119,60):

```python
from decimal import Decimal
from types import SimpleNamespace

from billing.invoice import format_invoice_total


def item(price, qty):
    return SimpleNamespace(price=Decimal(price), qty=qty)


def test_format_invoice_total_includes_vat_and_german_formatting():
    assert format_invoice_total([item("1000", 1)]) == "1.190,00 EUR"


def test_format_invoice_total_rounds_half_up():
    assert format_invoice_total([item("100.50", 1)]) == "119,60 EUR"
```

I used `SimpleNamespace` because I don't know your item type. Swap in the real one if you have it.