I added `format_invoice_total`, which composes the two existing functions:

```python
def invoice_total(items) -> Decimal:
    return calc_net(items) + calc_vat(items)


def format_invoice_total(items, currency: str = "EUR") -> str:
    return format_currency(invoice_total(items), currency)
```

The new function goes directly below `invoice_total`. Nothing else in the file changes.

- **Rounding:** `invoice_total` returns an unrounded `Decimal`, and `format_currency` already rounds with `ROUND_HALF_UP`. The footer string therefore rounds only once, at the end, and matches the existing display behavior.
- **Currency:** The `currency` parameter defaults to `"EUR"`, like `format_currency`, so the PDF footer call is just `format_invoice_total(items)`.
- **Format:** For a gross total of `Decimal("1234.50")` it returns `1.234,50 EUR`.

I couldn't run anything in this session, so this is untested. A focused test could look like this:

```python
def test_format_invoice_total_uses_german_separators():
    items = [SimpleNamespace(price=Decimal("1000.00"), qty=1)]
    assert format_invoice_total(items) == "1.190,00 EUR"
```

I left the terse names in `calc_net` and `calc_vat` (`t`, `i`) alone, since renaming them is outside this request. I can tidy them in a separate change if you'd like.