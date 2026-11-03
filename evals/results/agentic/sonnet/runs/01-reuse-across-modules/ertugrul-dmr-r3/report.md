The confirmation email in `shop/emails.py` now has a line like `Gesamtbetrag: 1.234,50 EUR` directly after the item list. I haven't run the tests or sent a sample email.

The amount comes from `gross_total(o)` in `shop/orders.py` and is formatted with `format_eur` from `shop/money.py`, the same formatter the shop already uses for money. The gross total includes VAT and shipping.

I didn't add a test for the new line.