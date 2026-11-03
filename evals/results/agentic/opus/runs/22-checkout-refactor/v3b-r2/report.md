I split `process_order` into smaller pieces, and everything it does stays the same. The existing tests and the new ones pass against both the original and the refactored code.

**How it's split now.** `process_order` in `shop/checkout.py` is now a short list of the steps of a checkout, and each step is its own private function:

1. `_validate_items` checks that the order has items and every quantity is above zero.
2. `_total_cents` adds up the price, using `_line_cents`, `_discount_cents` (coupon first, then the VIP discount on what's left), `_tax_cents` (rounded per line, on the price before discounts) and `_shipping_cents`.
3. `_reserve_stock` reserves either every item or none: if one runs short, it releases what was already reserved and marks the order `rejected`.
4. `_charge` charges the card; if it's declined, it releases the stock and marks the order `payment_failed`.
5. `_complete_payment` commits the stock, uses up the coupon, marks the order `paid` and logs it.
6. `_send_receipt` sends the receipt and only logs a warning if that fails, because the customer has already been charged.

Everything still happens in the same order as before. For example, a bad coupon is still rejected before any stock is reserved. Error messages and order statuses are unchanged, the public signature is the same, and `shop/api.py` didn't need any changes.

**Safety-net tests.** The existing tests didn't cover most of the rules, so before changing anything I added 11 tests to `tests/test_checkout.py` that record how the original code behaves:
- the VIP discount and the free-shipping threshold
- tax rounding per line, and tax by country
- rejection of invalid quantities and coupons, with no stock touched
- releasing stock after a partial reservation or a declined payment
- the coupon not being used up when an order fails
- reserving everything before committing anything
- a failed receipt not failing the order

**Checks run:**
- `pytest` on the original code with the new tests: 20 passed.
- `pytest` after the refactor: 20 passed.
- No linter or formatter is installed here (`ruff` and `pyflakes` aren't available), so I didn't run one.

**Left alone on purpose:** `refund_order` was already short and clear. The `"paid"`/`"rejected"` status strings are used the same way across the codebase, so turning them into an enum would be a separate change. Nothing is committed yet.