I've refactored `process_order` into a short list of named steps. All 22 tests pass, the 9 existing ones plus 13 new ones I wrote for paths that had no tests.

**Testing first.** The existing tests didn't cover VIP discounts, the free-shipping threshold, invalid or used-up coupons, invalid quantities, per-line tax rounding, undoing a partial stock reservation, or a failed receipt send. So before changing anything, I added `tests/test_checkout_characterization.py` to record how the current code behaves on those paths, including the exact order of reserve/release/commit calls. All 13 passed on the original code and still pass after the refactor.

**The refactor** (`shop/checkout.py`). `process_order` now reads as six steps:

```python
_validate_items(order.items)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_finalize_paid_order(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

The price calculation is split further into `_subtotal_and_tax`, `_discount` and `_shipping`, and `_release` is shared by the out-of-stock and payment-declined paths. The function's signature, return value, error messages, log messages and the order of external calls are all unchanged. Some existing quirks are now pinned by tests and I kept them as they are:
- If an order is rejected for invalid items or an invalid coupon, its status stays `"new"`.
- The VIP discount applies to the price after the coupon discount.
- Free shipping is decided on the discounted price before tax, starting at exactly 5000 cents.
- The coupon is only redeemed after the payment succeeds.
- If the receipt fails to send, the error is logged and the order still counts as paid.

One existing gap I left alone: if `inventory.reserve` raises anything other than `OutOfStock`, the items already reserved aren't released. That was true before and is still true. If you'd like, I can fix it as a separate change.

Nothing is committed. Both files are uncommitted changes in your working tree for you to review.