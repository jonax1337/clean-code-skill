The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line directly after the item list, followed by the existing blank line. `pytest` shows 9 passed.

The total comes from the existing `gross_total(order)`, which is net plus VAT (rounded per line) plus shipping. It's formatted with the shop's `format_eur`, the same helper `receipts.py` uses. The change in `shop/emails.py` is the two imports and one added line.

I added a test in `tests/test_emails.py` for an order with shipping. It checks that the line appears right after the items with the expected amount.

The total includes shipping, as you asked for the gross total. The email still doesn't show a separate shipping line.

I haven't committed anything.