The order confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line directly after the item list, followed by the existing blank line. The full test suite passes (9 tests, run with pytest).

- **Total:** it comes from the existing `gross_total(order)` in `shop/orders.py`, so it is net plus per-line VAT plus shipping.
- **Format:** it uses the shop's existing `format_eur` from `shop/money.py`.
- **Test:** I added `test_body_shows_gross_total_right_after_items` in `tests/test_emails.py`. It uses an order with a reduced-VAT item and 4.90 shipping, and expects `Gesamtbetrag: 37,00 EUR` right after the item line.

The total includes shipping. The email's item list doesn't show shipping on its own line, so a customer adding up the items may see a total higher than their sum.