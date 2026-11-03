I split `process_order` into small private helpers, and all 26 tests pass (`python -m pytest -q`). That includes the 9 original tests, which pass unchanged. I didn't run a linter or type checker, and I haven't committed anything.

**The refactor (`shop/checkout.py`)**
`process_order` is now a short outline that reads top to bottom:
```
_validate_items → _price_order → _reserve_stock → _charge → _complete_order → _send_receipt
```
- **Pricing:** `_price_order` calls `_tax_cents` and `_discount_cents`.
- **Stock release:** the duplicated "give the stock back" loop is now `_release_stock`.
- **Unchanged:** the public signature, the constants, `refund_order`, the order of side effects, the error messages and the `status` values.
- **Added import:** I added `Item` to the `shop.models` import for type hints.

**Tests added**
The existing tests didn't cover most of the tricky parts, so I added `tests/test_checkout_pricing_and_rollback.py` before touching the code. All 17 new tests passed against the original code first, so they describe what it did before I changed it. They cover:
- Invalid quantities, and unknown or used-up coupons.
- Tax rounded half-up per line.
- The VIP discount, and VIP stacked on a coupon.
- The free-shipping threshold, just below and exactly at it, and judged after discounts.
- Tax rates for FR, CH and an unknown country.
- Stock rollback after a partial reservation and after a declined payment.
- The coupon only being used up on a successful payment.
- A failing receipt email not failing the order.

**Left alone**
- `refund_order`, `shop/api.py` and the other modules.
- A few details of the existing behavior that you may find surprising:
  - An invalid coupon or quantity leaves `order.status` as `"new"`.
  - Tax is charged on the undiscounted price.
  - `_send_receipt` swallows every exception on purpose, as the original did.