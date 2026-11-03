I've refactored `process_order` in `shop/checkout.py`. It's now a short list of steps, each handled by a small private helper:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, total)
_complete_payment(order, inventory, coupons, total)
_send_receipt(notifier, customer, order, receipt_id)
return receipt_id
```

All 21 tests pass on both the old and the new code. Nothing is committed yet.

**How I checked that behavior didn't change:** the existing 9 tests didn't cover much, so I first added 12 tests to `tests/test_checkout.py` and ran them against the original code, where they all passed. Then I refactored and ran them again. They cover:
- VIP discount applied on top of a coupon
- tax charged on the price before discounts and rounded per line
- the free-shipping threshold (at it, just below it, and pushed below it by a discount)
- invalid coupon and zero quantity rejected before any stock is reserved
- stock released when only part of an order could be reserved
- coupon not used up when payment is declined
- the order of stock and coupon changes on success
- a failed receipt email not failing the order

Calls to the payment gateway, inventory and coupons happen in the same order as before, so things like an invalid coupon being rejected before any stock is reserved still hold.

**What changed (Clean Code rule numbers):**
- **G30/G34:** each helper does one thing at one level of detail. Pricing is split into `_tax_cents`, `_discount_cents`, `_coupon_discount_cents` and `_shipping_cents`.
- **G5:** the two copies of the "release stock" loop are now one `_release_stock`. When a payment is declined, every item has already been reserved, so releasing `order.items` does exactly what the old `reserved` list did.
- **C3/C4:** the inline comment about tax became the docstring of `_tax_cents`. I added two short docstrings for rules that aren't obvious: the VIP discount comes off the price left after the coupon, and a failed receipt email doesn't undo a payment.

**What I left alone:**
- **F1:** `process_order` still takes 6 arguments, because changing them would break `shop/api.py` and anything else that calls it. `_charge` (5 arguments) and `_discount_cents` (4) are also over the limit. Bundling the services into a dataclass would fix this, but it's an interface change, so it should be its own step.
- **P2:** status values like `"paid"` and `"rejected"` are still plain strings. A `StrEnum` would be cleaner, but it also affects `refund_order`, `Order` and the API output, so it's a separate change.
- Two of the new tests read `CouponBook._remaining` directly to check that a coupon wasn't used up, because `CouponBook` has no public way to ask.

Want me to commit this on a branch?