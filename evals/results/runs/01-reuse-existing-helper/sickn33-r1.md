I added `format_invoice_total` at the end of the file. It reuses `invoice_total` and `format_currency`, so the rounding and German number format stay in one place.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    return format_currency(invoice_total(items), currency)
```

Example: if the gross total is `Decimal("1234.50")`, it returns `"1.234,50 EUR"`.

- **Rounding:** `invoice_total` doesn't round, and `format_currency` rounds half-up to 2 decimals once at the end. The footer therefore shows the rounded unrounded-gross total. If your invoice rounds VAT per line or on the VAT amount, the footer could differ by a cent from the printed lines. Let me know if you need that.
- **Scope:** I left the existing names (`calc_net`, `calc_vat`, `t`, `i`) alone, since you only asked for the new function.
- **Tests:** I couldn't run anything here. A focused test would be something like `format_invoice_total([Item(Decimal("1037.39"), 1)])`, whose net × 1.19 is 1234.4941 and should give `"1.234,49 EUR"`. Adding a half-cent case would also pin down the rounding.