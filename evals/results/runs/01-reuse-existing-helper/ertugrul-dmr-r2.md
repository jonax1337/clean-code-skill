I added `format_invoice_total`, which composes the existing `invoice_total` and `format_currency`, so no formatting logic is duplicated (G5).

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    return format_currency(invoice_total(items), currency)
```

For example, a gross total of `Decimal("1234.495")` renders as `1.234,50 EUR`. Rounding happens once, in `format_currency`, so there's no intermediate rounding error.

- **Name (G20, N1):** `format_invoice_total` says what it returns, and its prefix matches `format_currency`.
- **Type hints (P3):** the new public function is annotated. I left `items` untyped to match the rest of the module, since I can't see the item class. If you have one, such as an `InvoiceItem` dataclass, I'd annotate `items: Iterable[InvoiceItem]` here and on the other functions.
- **Existing code I didn't touch:** `calc_net` uses single-letter names (`t`, `i`), which is an N1 violation. It could become `sum((item.price * item.qty for item in items), Decimal("0"))`. I kept it out of this change, but I can do it separately if you want.