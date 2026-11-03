I've refactored `process_order` in `shop/checkout.py`, and all 21 tests pass on both the original and the refactored code. Nothing is committed yet.

**Tests first.** The existing tests didn't cover many of the paths a refactor could break without anyone noticing. So before changing anything I added `tests/test_checkout_characterization.py`, which records what the current code does in these cases:
- the VIP discount on top of a coupon, and discounts rounding down
- free shipping starting at exactly 5000 cents
- tax rounded half-up on each line rather than on the total (28.5 → 29 per line), and the default tax rate for unknown countries
- zero or negative quantities, and invalid or used-up coupons, being rejected before any stock is touched
- the exact order of reserve, release and commit calls, including giving back earlier reservations when a later item is out of stock
- a declined payment not using up the coupon
- a failed receipt not failing the order, with the log messages exactly as before

All 12 new tests passed on the old code. That confirms they describe how it behaves now, not how I assumed it would.

**The refactor.** `process_order` is now a short list of steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_complete_order(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
```

The pricing is split into `_tax_cents`, `_discount_cents` and `_shipping_cents`, and both rollback paths now share `_release_stock`. Every check, calculation, error message, status value and log line is the same as before, and they all happen in the same order. The public interface (`process_order`, `refund_order`) is unchanged, so `shop/api.py` needs no changes.

ruff isn't installed here, so I couldn't run the linter.