I added `invoice_footer_total` to `billing/invoice.py`. It reuses `invoice_total` and `format_currency`, so the footer follows the same VAT and rounding rules as the rest of the module.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def invoice_footer_total(items, currency: str = "EUR") -> str:
+    """Gross invoice total formatted for display, e.g. '1.234,50 EUR'."""
+    return format_currency(invoice_total(items), currency)
```

For example, net items totaling `1037.4790...` gross would render as `1.234,50 EUR`, with `.` as the thousands separator and `,` as the decimal separator, as `format_currency` already does.

`invoice_total` doesn't round the net or VAT separately. It adds the unrounded values and rounds once, in `format_currency`. If your invoices need VAT rounded to cents before summing (some accounting setups require this), the footer could differ by a cent from the line-level figures. If so, `calc_vat` should quantize its result, which would be a separate change.