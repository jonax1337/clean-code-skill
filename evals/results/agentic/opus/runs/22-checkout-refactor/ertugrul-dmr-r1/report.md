I've split `process_order` into small helpers, and its behavior is unchanged. All 21 tests pass. I haven't committed anything.

**Tests first.** The existing tests didn't cover much of the risky logic, so before touching the code I added `tests/test_checkout_characterization.py` (12 tests) and ran it against the **original** function. It passed. The tests lock in:
- **VIP discount:** applied after the coupon, with integer floor rounding.
- **Free shipping:** applies at exactly 5000 cents after discount, but not at 4999.
- **Tax:** rounded half-up on each line rather than on the total (the CH 40.5 → 41 case), plus the fallback rate for unknown countries.
- **Rejections:** invalid quantity and invalid coupon both reject the order without touching stock or charging. The status stays `"new"`.
- **Stock rollback:** if an item is out of stock, only items already reserved are released. A declined payment releases everything and doesn't use up the coupon.
- **Success path:** the exact order of reserve/commit calls in the inventory log, and the coupon is redeemed once.
- **Receipt failure:** if the receipt can't be sent, it's logged as a warning and the order still counts as paid.

**The refactor.** `process_order` now reads as six steps:
```python
_validate_items(order.items)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer.email, total, gateway, inventory)
_complete_paid_order(order, total, inventory, coupons)
_send_receipt(notifier, customer.email, order.id, receipt_id)
```
Pricing is split into `_line_cents`, `_tax_cents`, `_discount_cents`, `_coupon_percent` and `_shipping_cents`.

Changes, by rule:
- **G30/G34:** each function now does one thing at one level of abstraction.
- **G5:** the release loop, which appeared twice, is now one function, `_release_stock`. The line-price calculation, also written twice, is now `_line_cents`.
- **C3/C4:** the tax-rounding comment became a docstring on `_tax_cents`. I added short docstrings for the non-obvious rules (VIP after coupon, all-or-nothing reservation, receipt failures only logged).
- **G8:** all helpers are private, so `shop/api.py` and other callers are unaffected.

**Left alone on purpose:**
- **Signature (F1):** `process_order` keeps its 6 parameters because `shop/api.py` and the tests call it as it is. Grouping them into an object would change the public interface, so that should be a separate decision.
- **Status strings (P2):** `"paid"`, `"rejected"` and the other statuses are still plain strings. An Enum would be cleaner, but `Order.status` is shared with `refund_order` and the API's JSON output, so it's also better as its own change.