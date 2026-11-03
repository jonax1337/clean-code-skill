The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line directly after the item list, before the "Wir melden uns…" paragraph. I haven't run the tests or sent a test email.

The amount comes from the existing `gross_total(order)`, so it includes VAT (rounded per line, as `orders.py` requires) and shipping. It's formatted with the shop's `format_eur`, so it looks like every other amount in the shop.

The change is in `shop/emails.py`, which now imports `format_eur` and `gross_total`.