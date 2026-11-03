The confirmation email now has a `Gesamtbetrag: 1.234,50 EUR` line directly after the item list, in `shop/emails.py`. The existing tests pass (8 passed). I didn't add a test for the new line, but I rendered a sample order by hand.

- **Amount:** It comes from the shop's existing `gross_total(order)`, so it includes VAT (rounded per line, as the tax advisor requires) and shipping.
- **Formatting:** It uses `format_eur` from `shop/money.py`, the same helper the rest of the shop uses for money.
- **Sample check:** A 1000 € net item with 44,50 € shipping printed `Gesamtbetrag: 1.234,50 EUR`.

The blank line that used to follow the item list now comes after the total, so the total sits right under the items.