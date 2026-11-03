The confirmation email in `shop/emails.py` now has a line like `Gesamtbetrag: 1.234,50 EUR` directly after the item list. I haven't run the tests or sent a test email.

The amount comes from the existing `gross_total(order)`, so it includes VAT (rounded per line) and shipping. It's formatted with the shop's `format_eur`.

I didn't add a test for the new line.