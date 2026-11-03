I split `process_order` in `shop/checkout.py` into small helper functions, and all 9 existing tests pass. I haven't committed anything.

`process_order` is now a short outline of the steps:

1. `_validate_items`
2. `_subtotal_and_tax`
3. `_discount_cents`
4. `_shipping_cents`
5. `_reserve_stock`
6. `_charge`
7. `_complete_order`
8. `_send_receipt`

I kept the original order of side effects and error checks. For example, tax is still computed before the coupon is checked. The arithmetic, status values, error messages, logging and the "receipt failure doesn't undo payment" behavior are unchanged. I also kept the tax-rounding comment and added a short note on why receipt errors are swallowed.

I only ran the existing tests, which cover the happy path, coupon, no items, out of stock, declined payment and refund. They don't cover VIP discounts, free shipping, invalid coupons, invalid quantities or a failing notifier. I read those paths through carefully, but the tests wouldn't catch a mistake there. I can add tests for them before you deploy if you'd like.