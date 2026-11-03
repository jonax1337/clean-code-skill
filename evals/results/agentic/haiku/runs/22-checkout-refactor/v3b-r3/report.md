`process_order` is now a short pipeline of named steps, and all 17 tests pass, including the 8 I added before changing anything.

**What changed in `shop/checkout.py`**

`process_order` now reads as: validate, compute the total, reserve stock, charge, complete the payment, send the receipt. The helpers are:

- `_validate_items`: empty-order and quantity checks.
- `_total_cents`: subtotal, tax, discount and shipping, combined into the total.
- `_line_tax_cents`: per-line tax rounding, with the original comment kept.
- `_discount_cents` and `_shipping_cents`: coupon, VIP and free-shipping rules.
- `_reserve_stock`: reserves each item and releases the partial reservation on `OutOfStock`.
- `_charge`: calls the gateway and releases the stock on `PaymentDeclined`.
- `_complete_payment`: commits stock, redeems the coupon, sets the status and logs.
- `_send_receipt`: still swallows and logs notifier failures.
- `_release_stock`: a small loop helper shared by the two rollback paths.

I kept the order of operations as it was. Tax is still computed before the coupon check, so the same exception would be raised first if both fail. `refund_order` is untouched.

**Tests**

I added 8 characterization tests to `tests/test_checkout.py`, covering the paths the existing tests did not reach: VIP discount, free shipping, per-line tax rounding, default tax rate for unknown countries, invalid coupon, zero quantity, rollback when a later item is out of stock, and a failing receipt not failing the order. They passed on the original code before I refactored.

- Before: 9 passed.
- After the refactor: 17 passed.

I did not run ruff, mypy or pyflakes because they are not installed here. The module compiles.

**Things I noticed but did not change**

- If `gateway.charge` raises something other than `PaymentDeclined`, the stock reservation stays held and the order stays `"new"`. The refactor preserves this, and one of the new tests pins the rollback behavior for the other paths, not this one. This may be a bug worth a separate ticket.

Nothing is committed.