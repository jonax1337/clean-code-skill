I refactored `process_order` in `shop/checkout.py` into smaller helpers. Behavior is unchanged as far as I can verify here.

**What changed**

`process_order` is now a short sequence of steps:

1. `_validate_items` checks for empty orders and non-positive quantities.
2. `_calculate_total` computes the amount to charge, using `_subtotal_and_tax` (per-line tax rounding), `_discount` (coupon and VIP), and the shipping rule.
3. `_reserve_stock` reserves items and rolls back on `OutOfStock`.
4. `_charge` calls the gateway and rolls back on `PaymentDeclined`.
5. `_complete_order` commits stock, redeems the coupon, sets the paid status, logs, and sends the receipt (receipt failures are still logged and swallowed).

`_release` is a small shared helper for the two rollback paths. The public signature, the exception types and messages, the status values, and the order of calls to the inventory, gateway, and coupon objects are all kept as before. I left `refund_order` alone.

**Verification**

- The existing test suite passes: 9 of 9, both before and after the change.
- Because the existing tests cover few paths, I also ran the original `process_order` (from `git show HEAD`) and the new one side by side on 20,000 randomized orders. The cases covered empty orders, bad quantities, unknown coupons, VIP customers, different countries, out-of-stock and declined payments, and receipt failures. Return values, raised exceptions and their causes, order status and total, and the full inventory, gateway, notifier, and coupon call logs all matched in every case. About 1,000 of those cases were successful checkouts and the rest were rejections, so the success path got less coverage than the rejection paths.

The fuzz script lives in a temp folder outside the repo, so nothing extra was added to the project. Nothing has been committed.