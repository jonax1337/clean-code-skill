The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line directly after the item list. `pytest` ran after my last edit: 9 passed. I didn't run a linter or type checker.

- **Amount:** it uses the shop's existing `gross_total(order)`, which is net plus VAT plus shipping. VAT is rounded per line, as the tax advisor requires.
- **Formatting:** it uses `format_eur` from `shop/money.py`, the same formatter the receipts use, so money looks the same everywhere.
- **Layout:** the blank line before "Wir melden uns…" is still there.
- **Test:** I added `test_body_shows_gross_total_with_shipping_after_items` in `tests/test_emails.py`. It checks a 1.000,00 net order with 19 % VAT and 4,50 shipping, which gives `1.194,50 EUR`, and that the line sits right after the item list.

I left the rest of `emails.py` alone, for example the string concatenation and `== None` checks.