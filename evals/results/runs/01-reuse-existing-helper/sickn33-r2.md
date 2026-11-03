I added a small function that composes the two existing helpers, so rounding and the German number format stay in one place (`format_currency`) and the gross calculation stays in `invoice_total`.

```diff
 def invoice_total(items) -> Decimal:
     return calc_net(items) + calc_vat(items)
+
+
+def format_invoice_total(items, currency: str = "EUR") -> str:
+    return format_currency(invoice_total(items), currency)
```

For example, a gross total of `Decimal("1234.5")` returns `"1.234,50 EUR"`, which is the format you want for the PDF footer.

- **Name:** `format_invoice_total` follows the verb style of `format_currency` and says it returns a display string. `invoice_total` still returns the `Decimal`, so numeric callers are unaffected.
- **Rounding:** `format_currency` rounds half-up to two decimals only at display time. The VAT amount isn't rounded before it's added to the net, which is the existing behavior, and I left it alone. If your invoices need VAT rounded per line or per invoice for legal reasons, that would be a separate change.
- **Scope:** I didn't rename `calc_net`, `calc_vat`, `t`, or `i`. They're a candidate for a later cleanup, but it would mix an unrelated refactor into this feature.

I haven't run anything, but a focused test would be:

```python
def test_format_invoice_total_uses_german_format():
    items = [SimpleNamespace(price=Decimal("1037.39"), qty=1)]  # 1037.39 * 1.19 = 1234.5041
    assert format_invoice_total(items) == "1.234,50 EUR"
```