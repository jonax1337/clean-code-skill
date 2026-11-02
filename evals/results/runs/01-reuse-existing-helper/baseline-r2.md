Add this function to `billing/invoice.py`, after `invoice_total`:

```python
def format_invoice_total(items, currency: str = "EUR") -> str:
    """Gross invoice total as a display string for the PDF footer, e.g. '1.234,50 EUR'."""
    return format_currency(invoice_total(items), currency)
```

The full change as a diff:

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    """Gross invoice total as a display string for the PDF footer, e.g. '1.234,50 EUR'."""
+    return format_currency(invoice_total(items), currency)
```

**How it works:** `invoice_total` already returns net plus VAT (the gross amount), and `format_currency` already handles the rounding (`ROUND_HALF_UP` to two decimals) and the German-style separators (`.` for thousands, `,` for decimals). The new function just composes the two, so the footer uses the same formatting as everything else.

**Note on rounding:** `calc_vat` isn't rounded on its own, so the gross total is computed at full precision and rounded only once at display time. If your invoices need VAT rounded to cents before it's added to the net (common for legal invoice requirements), the displayed total could differ by a cent from the sum of the displayed net and VAT lines. If that matters, `calc_vat` should quantize its result, but I left that unchanged since you only asked for the footer string.