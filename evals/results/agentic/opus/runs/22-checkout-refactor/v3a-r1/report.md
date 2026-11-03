I split `process_order` into small steps. Its signature, its behavior and the public API are unchanged. All 20 tests pass, but I couldn't run a linter or type checker because neither ruff nor mypy is installed here.

**Tests first.** The 7 existing checkout tests didn't cover a lot of the pricing and failure logic. I added 11 tests to `tests/test_checkout.py` that capture what the original code does, and ran them against the unchanged code first (all passed). They cover:
- VIP discount applied after the coupon discount
- free shipping from exactly 5000 cents, using the price after discounts
- tax rounded half-up per line, and the tax rate following the customer's country
- an item quantity of 0 or less, and an invalid coupon: both reject the order before any stock is touched, and the status stays `"new"`
- out of stock: items already reserved are released
- declined payment: the coupon is not redeemed
- the exact order of reserve and commit calls
- a failed receipt email is logged and does not fail an order that's already paid

**The refactor** (`shop/checkout.py`). `process_order` now reads as six steps:

```python
_validate(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, gateway, inventory)
_complete(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

The price is split into `_tax_cents`, `_discount_cents`, `_coupon_percent` and `_shipping_cents`. `_release_stock` replaces the release loop that appeared twice. I kept the existing comment about per-line tax rounding. Where the reason for a rule isn't obvious from the code, I added a one-line docstring: stacking the VIP discount on the coupon, all-or-nothing reservation, and the deliberate catch-all around the receipt.

**Checks:**
- Before the refactor: 9 passed. After adding the tests: 20 passed. After the refactor: 20 passed.
- Not run: ruff and mypy, because neither is installed in this environment.
- The checkout code grew by about 20 lines, mostly function headers and docstrings.

**Left alone:**
- `refund_order` and `shop/api.py`: they're outside the task.
- `_charge` takes 5 arguments. Reducing that would mean a parameter object for a private helper, which I didn't think was worth it.
- In the existing `test_coupon_discount_is_applied_and_redeemed`, the test calls `coupons.redeem("SPRING10")` itself, so it doesn't really prove that checkout redeems the coupon. The new `test_paid_order_commits_stock_and_redeems_the_coupon` covers that properly. You may want to fix the old test.

Nothing is committed yet.