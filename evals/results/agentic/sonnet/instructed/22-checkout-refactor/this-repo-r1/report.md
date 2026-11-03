I split `process_order` in `shop/checkout.py` into small private helpers, and behavior is unchanged. All 19 tests pass, the 9 that were already there and 10 new ones.

`process_order` itself is now a short outline of the steps, in the original order:
- `_validate_items`
- `_order_total`, which uses `_subtotal_and_tax` and `_discount`
- `_reserve_stock`
- `_charge`
- `_complete_order`
- `_send_receipt`

The stock-release loop that appeared twice is now `_release_stock`.

Before changing anything, I added 10 characterization tests to `tests/test_checkout.py`, because the existing tests left most branches uncovered. They cover:
- per-line half-up tax rounding
- tax by country, including the default rate
- VIP discount stacked on a coupon
- the free-shipping threshold
- non-positive quantities
- an unknown coupon
- rollback of partially reserved stock
- a failing receipt email not failing the order

They passed against the original code first, then again after the refactor.

The public signature of `process_order` is unchanged, and `api.py` and `refund_order` are untouched. I did not run the code against the real gateway, inventory or notifier, only the test fakes.

I did not change anything I noticed along the way:
- The helpers pass state through `order.status` and `order.total_cents` as before.
- A declined payment still releases stock before setting the status, as it did originally.

I haven't committed anything.