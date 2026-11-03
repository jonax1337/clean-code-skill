I added `format_invoice_total`, which composes the existing `invoice_total` and `format_currency`:

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    return format_currency(invoice_total(items), currency)
```

For example, items summing to a gross total of `1234.5` give `"1.234,50 EUR"`.

- **No duplication (G5):** it reuses `invoice_total` and `format_currency` instead of re-implementing the calculation or the German number formatting.
- **One thing per function (G30):** it only joins the two steps, and rounding stays inside `format_currency`.
- **Currency parameter:** `currency` is passed through with the same default as `format_currency`, so the footer and other callers stay consistent. This is a value, not a flag argument (F3).

Existing issues I left alone, since you only asked for the new function:
- **P3:** `calc_net`, `calc_vat`, `invoice_total`, and my new function take an untyped `items`. I don't know your item type, so I matched `invoice_total`. A small `Protocol` with `price: Decimal` and `qty: int` would fix all four at once.
- **N1:** `t` and `i` in `calc_net` are terse names for a loop that isn't tiny. `total` and `item` would read better, or use `sum(item.price * item.qty for item in items)`.
- **G25:** `Decimal("0.01")` in `format_currency` could be a named constant such as `CENT`.

I can make those changes in a follow-up if you want.