The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line right after the item list. All 10 tests pass, including two new ones for it.

- **Change in `shop/emails.py`:** the amount comes from the existing `gross_total(o)`, so it includes VAT (rounded per line) and shipping. It is formatted with the shop's `format_eur`, so it looks like the rest of the shop. The existing blank line after the item list is kept, so the total sits directly under the items.
- **Tests in `tests/test_emails.py`:** one checks that the total follows the last item line directly and includes VAT and shipping (37,10 EUR). The other checks the thousands separator (1.190,00 EUR).

I didn't send a real email or look at the rendered output beyond what the tests assert.