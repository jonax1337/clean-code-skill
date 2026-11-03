The confirmation email in `shop/emails.py` now has a `Gesamtbetrag: 1.234,50 EUR` line right after the item list. I haven't run the tests or sent a sample email.

The amount is `gross_total(o)` from `shop/orders.py`: net, plus per-line VAT, plus shipping. It's formatted with the shop's existing `format_eur`, so it matches the other money output. I imported both and wrote no new logic.

The line comes straight after the item list, before the existing blank line.