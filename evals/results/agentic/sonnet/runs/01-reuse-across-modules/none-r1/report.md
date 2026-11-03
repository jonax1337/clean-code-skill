The confirmation email in `shop/emails.py` now has a `Gesamtbetrag: 1.234,50 EUR` line right after the item list. I haven't run the tests or sent a test email.

The amount comes from `gross_total(o)`, the same function the receipt uses for its `Summe` line. It includes VAT and shipping. It's formatted with `format_eur` from `shop/money.py`, so it looks like the amounts in the receipt.

I put the new line before the existing blank line, so the item list and the total sit together.