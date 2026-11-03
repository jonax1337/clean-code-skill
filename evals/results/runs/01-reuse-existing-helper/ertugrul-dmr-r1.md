I added `format_invoice_total` at the end of `billing/invoice.py`. It reuses `invoice_total` and `format_currency`, so the rounding and German-style number formatting stay in one place (G5).

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items) -> str:
+    return format_currency(invoice_total(items))
```

For a gross total of `1234.5`, `format_invoice_total(items)` returns `"1.234,50 EUR"`. `format_currency` rounds half-up to two decimals and defaults to EUR, so the footer string needs no extra handling.

I didn't change any existing code, but I noticed a few things in the file:

- **N1/N5:** `calc_net` uses `t` and `i`. Names like `total` and `item` would be clearer.
- **P3:** `items` has no type hint on the public functions `calc_net`, `calc_vat`, `invoice_total`, and the new `format_invoice_total`. I left it off the new function to match the existing ones. If you have an `InvoiceItem` type, I'd add `Iterable[InvoiceItem]` to all four.
- **G16:** The chained `.replace(",", "X")...` in `format_currency` hides its intent. A small named helper such as `_to_german_separators` would make it clearer.

I can apply any of these if you want.