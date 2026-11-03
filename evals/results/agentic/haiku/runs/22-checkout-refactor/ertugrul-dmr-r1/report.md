I refactored `process_order` in `shop/checkout.py` into small helpers. The public signature and behavior are unchanged, and I didn't commit anything.

**Structure now**

`process_order` reads as the checkout steps in order:

```python
_validate_items(order)
subtotal, tax = _price_items(order.items, customer.country)
discount = ...        # coupon, then VIP
shipping = _shipping_cents(subtotal - discount)
total = subtotal - discount + tax + shipping
_reserve_stock(order, inventory)
try: receipt_id = gateway.charge(...)
except PaymentDeclined as error: _abort_declined_payment(order, inventory, error)
_commit_stock(order.items, inventory)
coupons.redeem(...)   # if a coupon was used
_mark_paid(order, total)
notifier.send_receipt(...)  # still best-effort, logs on failure
```

New helpers: `_validate_items`, `_price_items`, `_coupon_discount`, `_shipping_cents`, `_reserve_stock`, `_abort_declined_payment`, `_release_stock`, `_commit_stock`, `_mark_paid`.

**Behavior preservation**

- The order of side effects is the same as before, including rollbacks on out-of-stock and on payment decline. The tax comment is kept with the pricing code.
- Exception types, messages, and `raise ... from` chaining are unchanged.
- `refund_order` and the constants are untouched.
- The `process_order` signature is the same, so callers aren't affected.

**Verification**

- Existing tests: 9 passed before and after.
- Differential check: I ran the original `HEAD` version and the new one on 20,000 randomized orders. The check compared return values, exceptions, order status and total, inventory log and state, gateway charges, notifier calls, and coupon usage. There were 0 mismatches. Most random cases were rejections (about 18.9k), so the successful path was exercised about 800 times and the gateway-failure path about 280 times.

**Choices you may want to revisit**

- `_abort_declined_payment` is typed `NoReturn` because it always raises.
- The coupon and VIP discount logic stays inline in `process_order`. Moving it out would need four arguments, which goes against the project's three-argument rule.
- I kept the receipt-sending `try` inline for the same reason.