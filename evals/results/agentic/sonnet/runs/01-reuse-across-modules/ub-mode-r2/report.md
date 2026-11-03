The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line right after the item list. The full test suite passes (9 tests).

- **Total:** it uses `gross_total` from `shop/orders.py`, so it includes VAT and shipping. The receipt's "Summe" line is built the same way.
- **Formatting:** it uses `format_eur` from `shop/money.py`, the same function the receipt uses.
- **Test:** I wrote the test first and watched it fail. It checks that an order with 1.234,50 EUR shipping shows `Gesamtbetrag: 1.266,60 EUR` directly under the item line.
- **Not done:** I haven't run the crapper, dryer or mutator tools, and I haven't committed anything.
- **Line endings:** git warns that `shop/emails.py` has CRLF line endings that it will convert to LF on the next commit.

**Log:**
1. I read the email, money, orders and receipt code to find the existing total and money formatting.
2. I added the failing test to `tests/test_emails.py`.
3. My first scripted edit only changed the imports and missed the body, because of the CRLF line endings. I made the body change with the Edit tool instead.