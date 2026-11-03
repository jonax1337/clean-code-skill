`process_order` is now split into named steps. All 19 tests pass, including 10 new tests I added first to pin behavior the existing suite didn't cover.

**What changed** (`shop/checkout.py`)

`process_order` now reads as six steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)
_mark_paid(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
```

The helpers are `_validate_items`, `_order_total` (which uses `_subtotal_and_tax`, `_discount_cents` and `_shipping_cents`), `_reserve_stock`, `_charge`, `_release_stock` (shared by the two rollback paths), `_mark_paid` and `_send_receipt`. The arithmetic, the order of operations, the error messages, the status values, the constants and the rounding comment are unchanged. `refund_order` and the public signatures are untouched.

**Tests added first** (`tests/test_checkout.py`)

I wrote these against the original code and they passed there, so they are a true baseline:
- Successful checkout reserves then commits stock (checked via `inventory.log`).
- Zero quantity is rejected.
- An unknown coupon is rejected before any stock is touched.
- VIP discount applies after the coupon.
- The free-shipping threshold is respected.
- Tax is rounded per line, not on the total.
- An unknown country uses the default rate.
- Out-of-stock releases the stock reserved so far.
- A declined payment releases stock.
- A failing receipt still returns the receipt id and leaves the order paid.

**Results**
- Before the refactor: `pytest` 9 passed.
- After adding the characterization tests, against the original code: 19 passed.
- After the refactor: 19 passed.

I did not run a linter or type checker; `pyflakes` isn't installed here. I checked the imports by reading the file.

**Choices you may want to revisit**
- `_charge` takes six parameters. That is more than the usual guideline, but a parameter object would add a type just for this one call, so I left it.
- I put the characterization tests in the same change as the refactor, so they're reviewed together. They're easy to split out if you prefer.