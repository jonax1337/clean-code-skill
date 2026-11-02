I added `format_invoice_total`, which formats the existing gross total with `format_currency`. The existing code is unchanged.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    """Gross invoice total as a display string for the PDF footer, e.g. '1.234,50 EUR'."""
+    return format_currency(invoice_total(items), currency)
```

- `invoice_total` returns net plus VAT, so this is the gross amount.
- `format_currency` rounds half-up to 2 decimals and uses German separators (`.` for thousands, `,` for decimals), which gives the `1.234,50 EUR` format.
- `currency` defaults to `"EUR"` but can be overridden.

`calc_vat` isn't rounded on its own, so the footer total is rounded once at the end. If your invoice also shows separate net and VAT lines that are each rounded for display, those lines may differ from the footer total by a cent. If that matters, round `calc_vat` to 2 decimals inside `invoice_total` so the displayed lines always add up.