I added `format_invoice_total`, which reuses `invoice_total` and `format_currency`, so the output matches your existing formatting (`.` for thousands, `,` for decimals).

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    """Return the gross invoice total as a display string, e.g. '1.234,50 EUR'."""
+    return format_currency(invoice_total(items), currency)
```

For example, if the gross total is `Decimal("1234.5")`, it returns `"1.234,50 EUR"`.

`invoice_total` doesn't round the VAT, so rounding happens only once, when the final amount is formatted. If the PDF also shows net and VAT as separately rounded lines, the footer could occasionally differ by one cent from their sum. If that matters, round `calc_vat` to 2 decimals inside `invoice_total`. I left that alone since it would change existing behavior.