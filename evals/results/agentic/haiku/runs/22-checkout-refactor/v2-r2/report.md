`process_order` in `shop/checkout.py` is now split into small named steps, and behavior is unchanged as far as the test suite can show. All 15 tests pass.

**What changed**

`process_order` now reads as a sequence of steps:
1. `_validate_items`
2. `_order_total`, which uses `_subtotal_and_tax`, `_discount_cents` and `_shipping_cents`
3. `_reserve_stock`
4. `_charge`
5. `_finalize_payment`
6. `_send_receipt`

Checks, side effects and the release-on-failure paths keep the original order. The per-line tax comment moved with its code, and `refund_order` is untouched.

**Tests**

The existing suite didn't cover several branches, so I added seven characterization tests to `tests/test_checkout.py` before refactoring:
- VIP discount
- free shipping at the threshold
- per-line tax rounding
- zero quantity rejected
- unknown coupon rejected
- a failing receipt doesn't fail the order

I worked out their expected values by hand. All 15 tests passed against the original code and still pass after the refactor.

**Caveats**

- In `_charge`, the payment-declined path releases `order.items`. The original released the `reserved` list, which at that point always equals `order.items`, so the result is the same.
- I couldn't run a linter or type checker because neither ruff nor mypy is installed here. Please run your usual checks before deploying.
- The new test file and the refactored module are uncommitted. I haven't committed anything.