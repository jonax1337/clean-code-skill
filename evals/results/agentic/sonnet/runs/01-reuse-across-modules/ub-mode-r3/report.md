The confirmation email now has a line like `Gesamtbetrag: 32,10 EUR` directly after the item list. The full test suite passes (9 tests).

- **Total:** it uses the existing `gross_total()`, so it includes VAT and shipping. The amount is formatted with `format_eur`, the same helper the receipts use.
- **Test:** I added a test in `tests/test_emails.py` and confirmed it failed before the change.
- **Commit:** the change is committed as `a2aeeaa`. I didn't push, because the repo has no remote configured.

**Log**
1. I read `shop/emails.py`, `shop/orders.py`, `shop/receipts.py` and `shop/money.py` to find the existing total and money-formatting code.
2. I wrote the failing test first.
3. My first scripted edit only changed the imports, because the file has CRLF line endings and the body replacement didn't match. I redid the body edit with the Edit tool.
4. I ran the tests and committed.

I didn't run the crapper, dryer or mutator tools, because the change is a single added line.