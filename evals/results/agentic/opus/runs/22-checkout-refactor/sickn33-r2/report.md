I've split `process_order` into small helpers, and it now reads as the six steps of a checkout:

```python
_validate_items(order.items)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete_order(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

Each step has its own function in `shop/checkout.py`. The pricing step is broken down further, into line price, tax, discount, coupon and shipping. The function's signature, its error messages, the status values and the order of calls to inventory, coupons, payment and the receipt sender are all the same as before.

**How I checked that behavior didn't change:** the existing tests left a lot of the risky logic untested. So before refactoring, I added `tests/test_checkout_characterization.py` and ran it against the **original** code first. It covers:
- the VIP discount applying after the coupon
- free shipping at exactly 5000 cents and not at 4999
- tax rounded per line, using a case where that gives a different total than rounding the sum
- invalid quantities and invalid coupons being rejected before any stock is reserved
- only the already-reserved items being released when a later item is out of stock
- the exact order of reserve and commit calls, and the coupon being redeemed once
- a receipt that fails to send not failing a paid order

All 18 tests passed before the refactor and still pass after it.

**Existing behavior I kept, which you may want to look at separately:** `_charge` only catches `PaymentDeclined`. If the payment gateway fails some other way (a timeout, a connection error), the stock stays reserved and the order stays `"new"`. That's how the original works, so I didn't change it, but it may be a production bug.

Nothing is committed yet. Tell me if you want it on a branch or in a PR.