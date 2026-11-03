I've split `process_order` into small helpers. All 27 tests pass (`pytest`: 27 passed), including 18 I added before refactoring. I didn't run a type checker or linter.

**Tests first.** The original 9 tests missed most of the pricing and rollback paths, so I added characterization tests and ran them against the unchanged code. They pass there, so they record what production does today. They cover:
- invalid quantities and invalid or used-up coupons
- the VIP discount, alone and stacked after a coupon
- the free-shipping threshold at 5000 and 4999, and the fact that it uses the discounted subtotal
- tax rounded half-up per line, and the tax rate for each country
- rolling back a partial stock reservation, and the exact order of inventory calls
- a declined payment leaving the coupon unredeemed
- a failing receipt send not failing the order

**Refactor in `shop/checkout.py`.** `process_order` is now a short sequence of steps:
1. `_validate_items`
2. `_price_order`, which uses `_discount_cents` and `_tax_cents`
3. `_reserve_stock`
4. `_charge`
5. `_complete_order`
6. `_send_receipt`

The order of side effects is unchanged: all validation and pricing happen before any stock is touched, and an invalid coupon still raises before reservation. Error messages, order statuses and log lines are the same. The one new thing is `_release_stock`, which replaces two copies of the same release loop. Public signatures are unchanged, and `refund_order` is untouched.

**Left alone.** I noticed that `process_order` isn't atomic if a later step fails. For example, if `inventory.commit` raised after the charge, the customer would be charged with stock still reserved. I kept that behavior because you asked for no changes, but it may be worth a separate look.

I haven't committed anything.