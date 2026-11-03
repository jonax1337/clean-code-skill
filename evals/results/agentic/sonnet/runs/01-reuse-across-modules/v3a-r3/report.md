The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line directly after the item list, with the blank line before the closing text kept as it was. I ran the tests and all 9 pass.

- **Amount:** it comes from the existing `gross_total` in `shop/orders.py`, so it includes VAT and shipping.
- **Format:** it goes through the existing `format_eur` from `shop/money.py`, so it matches the rest of the shop.
- **Test:** I added `test_body_shows_gross_total_right_after_items` in `tests/test_emails.py`. It uses a 1000,00 net item with 4,50 shipping and checks for `Gesamtbetrag: 1.194,50 EUR` right after the item line.

The change itself is in `shop/emails.py`. I haven't committed anything.