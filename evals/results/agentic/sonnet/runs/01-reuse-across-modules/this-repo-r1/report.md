The confirmation email now has a line like `Gesamtbetrag: 1.194,90 EUR` directly after the item list. A blank line follows it, before the closing text. `pytest` gives 9 passed. I ran nothing else, so there was no linter or type check.

The amount comes from the existing `gross_total()` in `shop/orders.py`, so it includes VAT and shipping. It is formatted with the shop's `format_eur()`, the same function `receipts.py` uses.

I added `test_body_shows_gross_total_right_after_items` to `tests/test_emails.py`. It uses a 1.000,00 EUR net item (standard VAT) plus 4,90 EUR shipping and expects `1.194,90 EUR`.