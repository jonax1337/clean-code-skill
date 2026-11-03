I split `process_order` in `shop/checkout.py` into named steps. The public signature and the `refund_order` function are unchanged, and I did not commit anything.

`process_order` now reads as six steps: validate items, compute the total, reserve stock, charge, complete the payment, and send the receipt. Each step has a helper with a name that says what it does. The helpers are `_validate_items`, `_order_total_cents` (with subtotal, discount, tax and shipping helpers beneath it), `_reserve_stock`, `_release_stock`, `_complete_payment` and `_send_receipt`.

Before refactoring, I added 10 characterization tests to `tests/test_checkout.py`. They cover branches the existing tests missed: invalid quantity, unknown coupon, VIP discount (alone and after a coupon), the free-shipping threshold, per-line tax rounding, rollback of earlier reservations when a later item is out of stock, a failing receipt notifier, and single-use coupons. I ran them against the original code first, and all of them passed.

Verification:
- `pytest`: 19 passed (9 existing and 10 new), on both the original and the refactored code.
- Differential check: I ran the original `HEAD` version and the new version on 20,000 random orders, covering coupons, VIP, declines, out-of-stock, receipt failures and inventory logs. Every result matched.
- Ruff and pyflakes are not installed here, so I did not run a linter.

Behavior that I preserved on purpose, which looks questionable:
- If the gateway raises something other than `PaymentDeclined`, or the reservation loop raises something other than `OutOfStock`, the stock already reserved is not released. The old code had the same gap, so I kept it, and I did not pin it in a test.