`process_order` is now split into small helpers in `shop/checkout.py`, and its observable behaviour is unchanged. I did not commit anything.

The main function now reads as the checkout steps in order:

```python
_validate_order(order)
subtotal, tax = _price_lines(order.items, tax_rate(customer.country))
discount = _coupon_discount(order, coupons, subtotal)
if customer.vip:
    discount += _vip_discount(subtotal - discount)
shipping = _shipping_cents(subtotal - discount)
total = subtotal - discount + tax + shipping

reserved = _reserve_stock(order, inventory)
receipt_id = _charge_reserved(order, customer, inventory, gateway, reserved, total)

_finalize_paid_order(order, inventory, coupons, total)
_send_receipt(notifier, customer, order, receipt_id)
return receipt_id
```

The helpers are `_validate_order`, `_price_lines`, `_coupon_discount`, `_vip_discount`, `_shipping_cents`, `_reserve_stock`, `_charge_reserved`, `_release_items`, `_finalize_paid_order` and `_send_receipt`. I also added the `Item` import they need. The tax-rounding comment moved to `_price_lines`.

**Verification**
- The existing test suite passes: 9 of 9.
- I kept a copy of the original file outside the repo and compared old and new side by side over 1,920 input combinations. The combinations covered coupons (valid, invalid, exhausted), VIP, three countries, empty orders, zero quantities, out-of-stock, payment declined, and a failing receipt notifier. For each one I compared the return value or exception, order status and total, gateway calls, notifier calls, and the full inventory log. All matched.

**Things to know**
- The existing tests don't cover VIP, invalid coupons, invalid quantities, or a failing notifier. The 1,920-case comparison did, but it lives outside the repo. If you want those cases kept, I can add a few focused tests to `tests/test_checkout.py`.
- The ordering of checks, stock release on failure, and charging before committing stock are all unchanged, including the quirk that a failed reservation releases only the items reserved before the failing one.