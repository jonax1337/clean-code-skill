I broke `process_order` into small steps. Its signature, return value, exceptions and side effects are unchanged. Before touching the code I added tests that pin down how it works today, and they pass both before and after the refactor.

**What `process_order` looks like now** (`shop/checkout.py`):

```python
_validate_items(order.items)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_mark_paid(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

Each step is a private function in the same module. The pricing logic is split into `_line_cents`, `_tax_cents`, `_coupon_discount_cents` and `_shipping_cents`. The duplicated "release reserved stock" loop is now one `_release_stock`. Everything still happens in the same order: validation and coupon checks run before any stock is touched, all items are reserved before the charge, and items are committed and the coupon redeemed only after payment succeeds. `refund_order` and the public API are untouched.

One equivalence to know about: on a declined payment I now release `order.items` instead of the local `reserved` list. By that point every item has been reserved, so the two lists are identical. A test checks the exact reserve/release sequence.

**Safety net:** the existing 9 tests didn't cover much of the function, so I added 14 to `tests/test_checkout.py`. They cover:
- invalid quantities and an invalid coupon, both rejected before stock is touched
- the VIP discount stacking on top of a coupon
- the free-shipping threshold at exactly 5000 / 4999, measured after discounts
- tax rounded half-up per line and charged on the undiscounted price
- the tax rate following the customer's country
- the order of inventory calls
- partial reservations released when something is out of stock
- the coupon not being used up on failure
- a failed receipt not undoing a paid order
- the log messages

**Verification:**
- All 23 tests pass on the original code and on the refactored code.
- I didn't run Ruff (it isn't installed here) or a type checker.
- One remaining risk: the tests use fakes. Anything the real gateway or notifier does beyond what the fakes model isn't exercised.
- Nothing is committed.

**Existing behavior I kept but you may want to look at** (each would be a real behavior change, so I didn't touch it):
- If `gateway.charge` raises anything other than `PaymentDeclined` (a timeout, say), the reserved stock is never released.
- The same happens if `inventory.reserve` raises anything other than `OutOfStock`.
- A rejected order with an invalid coupon or quantity keeps status `"new"`, while out-of-stock sets `"rejected"`.

The pricing helpers could also move into `shop/pricing.py` next to `tax_rate`. I kept this change to one file.