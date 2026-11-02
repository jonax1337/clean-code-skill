# Reuse existing helper (Python)

Tests: search before you write (G5), scope discipline, no speculative options.

## Prompt

This is `billing/invoice.py` in our project:

```python
from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal("0.19")


def format_currency(amount: Decimal, currency: str = "EUR") -> str:
    quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{quantized:,.2f} {currency}".replace(",", "X").replace(".", ",").replace("X", ".")


def calc_net(items):
    t = Decimal("0")
    for i in items:
        t = t + i.price * i.qty
    return t


def calc_vat(items):
    return calc_net(items) * VAT_RATE


def invoice_total(items) -> Decimal:
    return calc_net(items) + calc_vat(items)
```

I need a function that returns the gross invoice total as a display string for the PDF footer, like `1.234,50 EUR`. Please add it and show me the change.

## Assertions

1. The new function calls the existing `format_currency` instead of reimplementing number formatting.
2. The new function calls the existing `invoice_total` (or the existing calc functions) instead of recomputing the total with new logic.
3. The existing functions `calc_net`, `calc_vat`, `invoice_total` and `format_currency` are left unchanged (no renames, no rewrites, no added type hints).
4. No speculative additions: no new classes, no new configuration parameters such as locale or rounding mode that were not asked for.
5. No comments that narrate the edit (e.g. "added new function", "uses existing helper").
