I split `process_order` into small helpers. Behavior should be unchanged, and all 19 tests pass. Nothing is committed yet.

**Tests first.** The existing tests didn't cover much of the function, so before changing anything I added 10 tests to `tests/test_checkout.py`. They record what the current code does, and they all passed against the original before I touched it. They cover:
- tax rounded per line, and tax rates by country
- the VIP discount applied after the coupon, with tax charged on the undiscounted price
- the free-shipping threshold, including exactly 5000 cents and dropping below it after a coupon
- invalid quantities and unknown or used-up coupons being rejected before any stock is reserved
- an out-of-stock order releasing only the items already reserved
- a declined payment releasing all items without using up the coupon
- the order of commits on success
- a failed receipt email not failing the order

**The refactor.** `process_order` now reads as the sequence of steps:

```python
_validate(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
return receipt_id
```

Pricing is split into `_line_cents`, `_tax_cents`, `_discount_cents` and `_shipping_cents`. A `_release` helper replaces the two copies of the stock-release loop. The public signature, error messages, status values and the order of side effects are all the same, so `shop/api.py` didn't need any changes. The comment explaining the tax rounding is still there, and I added two short docstrings that explain *why* (for example, why a failed receipt is only logged).

**Things I noticed but didn't change:**
1. **Possible stuck stock in production:** if `gateway.charge` raises anything other than `PaymentDeclined` (a timeout or connection error, say), the reserved stock is never released and the order status stays `"new"`. The original code had the same behavior and I kept it. It's probably worth a separate fix.
2. `test_coupon_discount_is_applied_and_redeemed` calls `coupons.redeem(...)` itself before checking the coupon is used up, so it doesn't really prove that `process_order` redeemed the coupon. It still passes and I left it alone.
3. Neither ruff nor pyflakes is installed here, so I couldn't run a linter or formatter. I checked imports and formatting by hand.

The diff is +164 / −15 lines: about +53 net in `checkout.py` and +111 in tests.