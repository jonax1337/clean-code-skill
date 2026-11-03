The confirmation email now has a `Gesamtbetrag: … EUR` line right after the item list. `pytest` gives 9 passed. I haven't run a linter or type checker.

- **Amount:** it uses the shop's existing `gross_total` (net, per-line VAT and shipping) and `format_eur`, so it looks like money elsewhere, e.g. `1.234,50 EUR`.
- **Layout:** the blank line after the items stays, so the total sits directly under the last item.
- **Test:** I added `test_body_shows_gross_total_right_after_items` in `tests/test_emails.py`. It uses an order that totals exactly 1.234,50 EUR.

The change is in `shop/emails.py`, which now imports `format_eur` and `gross_total`. I haven't committed anything.