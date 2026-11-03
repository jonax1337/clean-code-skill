The confirmation email now has a `Gesamtbetrag: …` line right after the item list, and the tests pass (`pytest`: 9 passed).

- **Change in `shop/emails.py`:** the line uses the existing `gross_total(order)` and `format_eur`, so it shows e.g. `Gesamtbetrag: 1.234,50 EUR`. That total includes VAT and shipping.
- **Test in `tests/test_emails.py`:** a new test checks the line sits directly after the item list. For a 30,00 net item at reduced VAT plus 4,90 shipping, it expects `37,00 EUR`.

I didn't touch anything else.