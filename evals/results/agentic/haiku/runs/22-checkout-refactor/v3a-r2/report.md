The refactor is done and all 18 tests pass. I didn't commit, since you didn't ask for one.

**What changed in `shop/checkout.py`**

`process_order` is now a short sequence of steps, each in its own private function:

- `_check_items`: rejects empty orders and non-positive quantities.
- `_price_order`: computes subtotal, tax, discount and shipping. The split is `_subtotal_and_tax` and `_discount_cents`, and the result is a small `_Amounts` dataclass with a `total_cents` property.
- `_reserve_stock`: reserves each item. On out-of-stock it releases what it reserved, sets `rejected`, and raises.
- `_charge`: charges the gateway. On decline it releases the stock, sets `payment_failed`, and raises.
- `_complete_order`: commits stock, redeems the coupon, and sets `paid` and the total.
- `_send_receipt`: sends the receipt and still logs and swallows any failure.
- `_release_stock`: the release loop, now shared by both rollback paths.

The order of operations, the arithmetic (including the per-line tax rounding and the integer floor division) and the messages are unchanged. `refund_order` and the constants are untouched.

**Tests**

Before refactoring I added 9 characterization tests for branches the suite didn't cover: zero quantity, unknown coupon, VIP discount alone and stacked on a coupon, the free-shipping boundary at exactly 5000, per-line tax rounding, partial-reservation rollback, no coupon redemption on decline, and a failing receipt not failing a paid order. All 18 tests passed against the original code first, then against the refactored code.

**Things to know**

- In `_charge`, the decline path releases `order.items` rather than the list of reserved items. That's equivalent because the charge only runs after every item has been reserved.
- Ruff and mypy aren't installed in this environment, so I didn't run lint or type checks. The tests are the only verification.
- The tests don't cover production data or the real gateway and notifier; they use the fakes in `tests/conftest.py`.