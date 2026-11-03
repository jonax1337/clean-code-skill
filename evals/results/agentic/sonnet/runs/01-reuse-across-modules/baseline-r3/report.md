The confirmation email in `shop/emails.py` now has a `Gesamtbetrag: 1.234,50 EUR` line right after the item list. I didn't run the tests or send a test email.

The amount comes from the shop's existing `gross_total(order)`, so it includes VAT and shipping. It's formatted with the shop's `format_eur`, which is what produces the German separators.

I put the line directly under the last item, with the blank line moved below it. If you'd like a blank line between the items and the total, that's a one-line change.