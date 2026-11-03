# Add a feature that needs helpers from other modules (Python)

Tests: search before you write (the money formatter and the total live in other modules and carry tax rules a reimplementation gets wrong), diff stays in scope inside a messy legacy file, a test for the new behavior, verified by running the tests.

## Prompt

Customers keep asking how much they paid. Please add the order's gross total to the order confirmation email in `shop/emails.py`, on its own line right after the item list, like `Gesamtbetrag: 1.234,50 EUR`. Money should look the same as everywhere else in the shop.
