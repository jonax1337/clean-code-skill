I split `process_order` into smaller steps, and nothing it does has changed. It now reads as six steps in a row:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)        # subtotal/tax → discount → shipping
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)
_complete_order(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
```

The pricing is split further into `_subtotal_and_tax`, `_discount` and `_shipping`. The two places that give stock back now share one `_release` helper. All the original logic, the order of checks and the error messages are moved over unchanged. The only other edit is adding `Item` to an import for the type hints. `process_order`'s signature is the same, so `shop/api.py` didn't need any changes.

**How I checked it:** the existing tests only covered the basic cases, so before changing any code I added `tests/test_checkout_characterization.py` (15 tests) to lock in the current behavior:
- rounding tax per line (half-up), and tax charged on the price before discounts
- the default tax rate for unknown countries
- the VIP discount applying after the coupon, rounded down
- the free-shipping cutoff at exactly 5000 cents, measured after discounts
- the exact rejection messages, and that a rejected order hasn't touched stock or status
- the order stock is reserved and released in when an item is out of stock or the payment is declined
- the coupon is used up only when the payment succeeds
- the log messages, and that a failed receipt email still leaves the order paid

All 24 tests (9 existing + 15 new) passed on the original code and still pass after the refactor.

**One thing I kept on purpose that you may want to look at:** if the payment gateway raises anything other than `PaymentDeclined` (a timeout, say), the reserved stock is never released and the order stays at status `"new"`. One of the new tests locks this in so the refactor couldn't change it quietly. It looks like a real bug, but fixing it would change production behavior, so it should be a separate change. I can do that next if you like.

I haven't committed anything.