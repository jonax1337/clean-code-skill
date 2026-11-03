The order confirmation email now has a `Gesamtbetrag: …` line directly after the item list. For a 30,00 EUR net item at the reduced VAT rate plus 4,90 EUR shipping, it reads `Gesamtbetrag: 37,00 EUR`. All 9 tests pass.

The amount comes from the existing `gross_total()` in `shop/orders.py`, so it includes per-line VAT and shipping. It's formatted with the existing `format_eur()` in `shop/money.py`, so it matches the shop's other amounts (`1.234,50 EUR`).

I changed two files:
- **`shop/emails.py`:** added the total line and the two imports it needs.
- **`tests/test_emails.py`:** added a test that checks the line appears right after the item list.