The confirmation email now has a `Gesamtbetrag: …` line directly after the item list. `python -m pytest -q` gives 10 passed.

- **Amount:** it is `gross_total(order)`, so it includes VAT (rounded per line) and shipping. It is formatted with `format_eur`, the same formatter `shop/receipts.py` uses. The change is in `shop/emails.py`.
- **Layout:** the blank line before "Wir melden uns…" is unchanged.
- **Tests:** I added two to `tests/test_emails.py`.
  - The first checks the exact line and position for a 30.00 net order with reduced VAT and 4.90 shipping, which gives `37,00 EUR`.
  - The second checks the thousands separator: a 1000.00 net item gives `1.190,00 EUR`.