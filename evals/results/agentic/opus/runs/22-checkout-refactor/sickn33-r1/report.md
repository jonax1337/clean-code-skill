I split `process_order` into smaller functions. The behavior is the same, and all 24 tests pass both before and after the change.

**How I checked it.** The existing tests only covered the basic paths. Before changing anything, I added `tests/test_checkout_characterization.py` with 15 tests that record what the original code does today:
- **Tax:** it's rounded half-up on each line, not on the total, and the rate depends on the customer's country.
- **Discounts:** the VIP discount is taken after the coupon, and tax is charged on the price before any discount.
- **Shipping:** it's free from 5000 cents, measured on the price after discounts.
- **Rejected orders:** a bad quantity, unknown coupon or used-up coupon is rejected before any stock is touched, and the order's status stays `"new"`.
- **Stock:** when an item is out of stock, only the items already reserved are released. When a payment is declined, every reservation is released and the coupon isn't used up.
- **Successful orders:** the stock steps (reserve, then commit) happen in the same order, and the coupon is used once per paid order.
- **Receipts:** if the receipt can't be sent, the paid order still succeeds and a warning is logged with the error details.

They all passed on the original code. I then refactored, and all 24 tests still pass.

**The new structure** (`shop/checkout.py`). `process_order` keeps its exact signature and now reads as the main steps in order:

```python
_validate_items(order.items)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_mark_paid(order, inventory, coupons, total)
_send_receipt(notifier, customer, order, receipt_id)
```

- **Pricing** is split into `_line_cents`, `_tax_cents`, `_discount_cents`, `_coupon_discount_cents` and `_shipping_cents`. Each can be read and tested on its own.
- **Stock and payment:** `_reserve_stock` and `_charge` keep their error handling and status changes. Both use a shared `_release_stock` helper instead of repeating the release loop.
- **Comments:** I kept the one about tax rounding for the accounting export, and added short docstrings where a rule isn't obvious from the code (how the discounts stack, why a failed receipt doesn't fail the order).

**One small difference to review.** When a payment is declined, the new code releases `order.items` instead of the list of reserved items. At that point every item has been reserved, so it releases exactly the same things, and a test checks this.

`refund_order` and `shop/api.py` are unchanged. I haven't committed anything; tell me if you'd like a branch and commit or a PR.