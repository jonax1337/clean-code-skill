I split `process_order` into smaller functions without changing behavior. All 19 tests pass. Nothing is committed yet.

**Tests first.** The existing tests only covered the happy path and a few failures, so I added 10 tests to `tests/test_checkout.py` covering what the function did before the refactor:
- an invalid quantity or an invalid coupon is rejected before any stock is reserved, and the order status stays `"new"`
- the VIP discount is applied after the coupon, and together they can bring an order up to free shipping
- free shipping starts at exactly 5000 cents (checked at 4999 and 5000)
- tax is rounded half-up per line, not on the total
- when an item is out of stock, items reserved before it are released and the coupon isn't used
- a declined payment doesn't redeem the coupon
- a paid order reserves every item, then commits every item, in that order
- a failing receipt sender only logs a warning, and the order stays paid

All 19 tests passed against the original code before I changed anything, and still pass after.

**The refactor** (`shop/checkout.py`). `process_order` is now six steps you can read top to bottom:

```python
_validate(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete_payment(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

The price calculation is split into `_line_cents`, `_tax_cents`, `_discount_cents` and `_shipping_cents`. The two duplicate loops that released stock are now one shared `_release_stock`. The signature is the same, so the one caller (`shop/api.py`) didn't need any changes.

Things that stay exactly as they were:
- the order of steps and of calls to the inventory, coupon and payment services
- error messages and status values
- the existing comment about per-line tax rounding

**Checks run:** `pytest` gave 19 passed. The project has no ruff or mypy configured, and neither is installed, so I ran no linter or type checker.

**Left alone:**
- `refund_order`: it's already short.
- The broad `except Exception` around sending the receipt: not failing a paid order is clearly intended there. I added a comment saying so.
- An existing test, `test_coupon_discount_is_applied_and_redeemed`, calls `coupons.redeem(...)` itself before its assertion. That makes it a check on `CouponBook` rather than on checkout, so it's worth tidying up separately.