The confirmation email now has a `Gesamtbetrag:` line directly after the item list, for example `Gesamtbetrag: 37,00 EUR`. I ran pytest and all 9 tests pass.

- **Total:** it uses the existing `gross_total(order)`, so it covers net, per-line VAT and shipping.
- **Format:** it goes through `format_eur` from `shop/money.py`, the same formatter used elsewhere in the shop.
- **Test:** I added `test_body_shows_gross_total_after_items` in `tests/test_emails.py`. It uses a 30,00 € reduced-VAT book plus 4,90 € shipping and expects 37,00 EUR.

The existing blank line after the total is unchanged.