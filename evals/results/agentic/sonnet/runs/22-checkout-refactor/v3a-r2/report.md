I split `process_order` in `shop/checkout.py` into small helpers, and its behavior is unchanged. All 22 tests pass (`pytest`). I did not run a linter or type checker, and I haven't committed anything.

`process_order` now reads as a short sequence: validate items, compute the total, reserve stock, charge, complete the order, send the receipt. The pieces are `_validate_items`, `_order_total`, `_tax_cents`, `_discount_cents`, `_reserve_stock`, `_release_stock`, `_charge`, `_complete_order` and `_send_receipt`.

- **Same behavior:** The order of side effects is the same. Validation and coupon rejection still happen before any stock is touched. Stock is reserved before the charge, and the coupon is redeemed only after a successful charge. A failed receipt is still only logged. Error messages and status values are unchanged.
- **Same interface:** The signatures of `process_order` and `refund_order` are unchanged, and I did not touch `refund_order`.
- **Rounding rule kept:** I kept the comment explaining that tax is rounded per line on the undiscounted price, and moved it to `_tax_cents`.
- **Extra tests:** The existing 9 tests missed many edge cases, so I first added 11 characterization tests in `tests/test_checkout_characterization.py`. I ran them against the original code, where they passed, and they still pass after the refactor. They cover:
  - invalid quantity and unknown coupon;
  - the VIP discount stacked on a coupon;
  - the free-shipping threshold, checked after discounts;
  - tax per country and half-up rounding per line;
  - stock release order on partial out-of-stock and on a declined payment;
  - the coupon not being redeemed on failure;
  - a receipt failure not failing the order.
- **Left alone:** I did not touch the other modules. One thing I noticed but didn't change, since it would alter behavior: `except Exception` around the receipt send is broad, but it looks intentional.