I split `process_order` into small helpers in `shop/checkout.py`. The public function and its signature are unchanged, and behavior is the same. All 14 tests pass: the original 9 plus 5 new regression tests.

`process_order` now reads as a short sequence:

```python
_validate_items(order)
subtotal, tax = _price_lines(order, customer)
discount = _discount(order, customer, subtotal, coupons)
shipping = _shipping(subtotal - discount)
total = subtotal - discount + tax + shipping

reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)
_complete_payment(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

The helpers stay in the same module, so the logger name and the module's imports are unchanged. The step order is also unchanged, including validation before tax, coupon checks before stock is reserved, and stock release on both failure paths.

To check the "behavior must not change" requirement, I ran the original function from git HEAD and the new one on 20,000 randomly generated orders. The inputs covered bad quantities, unknown and exhausted coupons, VIP customers, out-of-stock items, payment declines, gateway crashes, and receipt failures. Return values, exception types and messages, inventory calls, order status and totals, gateway calls, and receipts all matched. That comparison script lives in a scratch folder outside the repo.

Changes in the repo:
- `shop/checkout.py`: the refactor.
- `tests/test_checkout.py`: 5 new tests covering VIP discount after a coupon, free shipping at the threshold, invalid coupon rejected before stock is reserved, non-positive quantity, and a receipt failure not failing a paid order. The old suite didn't cover these branches.

Nothing is committed. Review the diff and commit when you're happy with it.