I split `process_order` into small helpers, and its behavior is unchanged. All 20 tests pass.

**How it reads now.** `process_order` (`shop/checkout.py`) is a short outline of the checkout:

```python
_validate_items(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_complete_payment(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

- **Pricing** is split into `_line_cents`, `_tax_cents`, `_discount_cents` and `_shipping_cents`. These only calculate and don't change anything. The note about rounding tax per line stays next to the tax code.
- **Stock and payment** live in `_reserve_stock`, `_charge` and `_complete_payment`. The "put reserved stock back" loop that was written out twice is now one function, `_release_stock`.
- The public signature, error messages, order statuses, log messages and the order of every call to inventory, gateway and coupons are exactly as before. `refund_order` and `shop/api.py` are untouched.

**Making sure nothing changed.** The existing tests didn't cover many of the paths a refactor could break. So before changing anything I added 11 tests to `tests/test_checkout.py` that capture what the code does today, and ran them against the original: 20 passed. They cover:
- per-line tax rounding and tax rates by country
- the VIP discount stacked on a coupon, and the free-shipping threshold
- invalid quantities and coupons, which are rejected before any stock is touched and leave the status at `"new"`
- partial reservations released when something is out of stock
- the coupon not being used up when payment fails
- the exact order of reserve and commit calls
- a failed receipt email being logged while the order stays paid

After the refactor, `pytest` still gives 20 passed.

**Not run:** ruff, mypy and pyflakes aren't installed here, so there was no lint or type check. You may want to run your CI linters before merging. I haven't committed anything.

**Left alone, but worth knowing:**
- `_send_receipt` still catches every `Exception` and only logs a warning. That's the current behavior, and probably on purpose, since the customer has already been charged. I added a one-line comment saying so.
- The existing `test_coupon_discount_is_applied_and_redeemed` calls `coupons.redeem(...)` inside the test, which makes it easy to misread. I left it as it is.