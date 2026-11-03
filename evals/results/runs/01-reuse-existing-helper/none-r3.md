I added `format_invoice_total` to `billing/invoice.py`. It reuses `invoice_total` and `format_currency`, so rounding and German number formatting stay in one place.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    """Gross invoice total as a display string for the PDF footer, e.g. '1.234,50 EUR'."""
+    return format_currency(invoice_total(items), currency)
```

- `invoice_total` returns net + VAT, which is the gross amount.
- `format_currency` rounds half-up to 2 decimals and formats with `.` as the thousands separator and `,` as the decimal separator, giving `1.234,50 EUR`.
- The `currency` parameter defaults to `"EUR"` and can be overridden.

Rounding happens only once, on the final gross amount. Net and VAT are not rounded separately. If the invoice needs to show net, VAT and gross lines that visibly add up, you may want to round each component first. Otherwise a footer total can differ by a cent from the sum of the displayed lines.