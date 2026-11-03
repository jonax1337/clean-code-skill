I added the gross total to the confirmation email in `shop/emails.py`. The existing 8 tests pass, but none of them cover the email body, so I didn't add or run a check that the new line appears.

The email now has a line like `Gesamtbetrag: 1.234,50 EUR` right after the item list, before the blank line. It uses the shop's existing `format_eur` and `gross_total`, the same ones `shop/receipts.py` uses. `gross_total` includes VAT and shipping, so the figure matches the "Summe" on the receipt.

I didn't add a test for the email body. I can add one if you want.