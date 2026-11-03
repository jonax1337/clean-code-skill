I added `invoice_total_display`, which wraps the existing `invoice_total` and `format_currency` so the footer string uses the same German formatting as the rest of the module.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def invoice_total_display(items, currency: str = "EUR") -> str:
+    """Gross invoice total formatted for display, e.g. '1.234,50 EUR'."""
+    return format_currency(invoice_total(items), currency)
```

`format_currency` rounds to two decimals with `ROUND_HALF_UP` and swaps the separators, so a gross total of `1234.5` renders as `1.234,50 EUR`.

`calc_vat` isn't rounded on its own, so rounding happens only once, on the gross total. If your invoice needs the VAT line rounded separately, so the printed net, VAT and gross add up exactly, the footer total could differ by a cent. In that case, quantize `calc_vat` before summing.