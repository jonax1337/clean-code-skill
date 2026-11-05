The confirmation email now has a `Gesamtbetrag: …` line directly after the item list. The full test suite passes, including a new test for this line.

The amount comes from `gross_total(order)`, so it includes VAT and shipping. It's formatted with the shop's existing `format_eur`, the same helper the receipts use. For the test order (30,00 net with reduced VAT, plus 4,90 shipping) the line reads `Gesamtbetrag: 37,00 EUR`.

The changes are in `shop/emails.py` and `tests/test_emails.py`.