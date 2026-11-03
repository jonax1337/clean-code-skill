`process_order` is now a short list of steps, and all 19 tests pass. I haven't committed anything.

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_complete_payment(order, inventory, coupons, total)
_send_receipt(notifier, customer, order, receipt_id)
return receipt_id
```

**What changed**
- In `shop/checkout.py` I moved each block of the old function into a private helper. The order total is built from `_line_cents`, `_tax`, `_discount` and `_shipping`. The two copies of the stock-release loop are now one `_release` helper.
- The code itself didn't change: rounding, the order of checks (an invalid coupon is still rejected before any stock is reserved), status values, error messages and log lines are all as before. The comment about rounding tax per line stays, next to the tax code.
- One spot looks different but isn't: when a payment is declined, the code now releases `order.items` instead of the `reserved` list. Payment only happens after every item has been reserved, so the two lists always hold the same items. A test checks this.
- The public signature of `process_order` is unchanged, so `shop/api.py` needed no changes.

**Tests to lock in current behavior**
The existing tests didn't cover a lot of this function. Before refactoring, I added 10 tests to `tests/test_checkout.py` and ran them against the original code (19 passed). They cover:
- the VIP discount applied after the coupon, with tax on the undiscounted price
- tax rounded half-up on each line, not on the whole order
- shipping exactly at the 5000-cent free-shipping limit and just below it
- zero quantities and invalid coupons being rejected with no side effects
- an out-of-stock item releasing only what was already reserved
- a declined payment releasing every item and not using up the coupon
- all items reserved before any are committed
- a failing receipt sender being logged while the order stays paid

After the refactor: `pytest` gave 19 passed. The project has no linter or type checker set up (ruff isn't installed), so I didn't run either.

**Line endings:** my rewrite script switched `checkout.py` to Windows (CRLF) line endings by accident. I converted it back to LF to match the repo and checked that it now has no CRLF.

**Left alone**
- `refund_order`, because it wasn't part of the request.
- The `except Exception` around sending the receipt. It hides every failure except the log line, but changing it would change production behavior. Decide on that separately.
- An odd existing test, `test_coupon_discount_is_applied_and_redeemed`, which calls `coupons.redeem(...)` itself before its last assertion. It doesn't really show that checkout used up the coupon; it may be worth fixing later.

Net change: `checkout.py` grew by about 32 lines, mostly function headers and blank lines, and the tests grew by 111 lines.