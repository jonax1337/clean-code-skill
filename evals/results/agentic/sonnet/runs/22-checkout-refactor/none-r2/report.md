I split `process_order` in `shop/checkout.py` into small helpers, and the existing 9 tests pass. I didn't commit anything.

`process_order` is now a short sequence of calls:
- `_validate_items`
- `_subtotal_and_tax`
- `_discount`
- `_shipping`
- `_reserve_stock`
- `_charge`
- `_finalize_order`
- `_send_receipt`

I kept the order of side effects the same, so behavior should be unchanged. The tax rate lookup still happens before coupon validation. Stock is still released and the order status set before each `OrderRejected`. A failed receipt send is still only logged. The tax comment moved into the docstring of `_subtotal_and_tax`.

The one structural change is a shared `_release` helper, which replaces the two identical release loops. I didn't touch `refund_order`.

I didn't check how thoroughly the tests cover the coupon, VIP, free-shipping and failure paths. Look at that before deploying.