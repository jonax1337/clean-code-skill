I split `process_order` in `shop/checkout.py` into smaller helpers. Behavior should be unchanged: the existing tests pass, and a differential check found no differences from the original.

`process_order` now reads as the checkout steps in order:

1. `_validate_items` checks for an empty order and non-positive quantities.
2. `_order_total` computes the amount to charge, using:
   - `_subtotal_and_tax`, which keeps the per-line tax rounding.
   - `_discount_cents`, which covers the coupon and VIP discounts.
   - `_shipping_cents`.
3. `_reserve_stock` reserves each item and releases any partial reservation if one is out of stock.
4. The charge stays inline in `process_order`, so the payment-declined path (release stock, set `payment_failed`, raise) is visible in one place.
5. `_commit_stock`, the coupon redemption, and the status and total updates stay in `process_order`.
6. `_send_receipt` sends the receipt and logs a failure without undoing the payment.

I also added a small `_release_stock` helper, used by both failure paths.

**Verification**
- `pytest`: 9 passed before and after the change.
- Differential check: I ran the original and refactored `process_order` on 3,000 randomly generated orders. The cases covered empty and invalid items, bad coupons, VIP customers, several countries, out-of-stock, declined payments, and failing receipts. For each case I compared the return value or exception (including its cause), the order status and total, the charges, and the stock levels. There were 0 mismatches. The check was a temporary script that I deleted afterwards.

I didn't touch `refund_order`, and I didn't commit anything. The change is only in `shop/checkout.py` and is uncommitted in the working tree.