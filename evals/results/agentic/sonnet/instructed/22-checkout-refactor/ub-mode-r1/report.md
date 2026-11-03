I split `process_order` in `shop/checkout.py` into small helpers, and its behavior hasn't changed. All 19 tests pass, including the 10 new ones, which also passed against the original code before I touched it.

`process_order` is now a short outline of the steps, and each step is a helper:

- **Validation and pricing:** `_validate_items`, `_subtotal_and_tax`, `_discount` and `_shipping` check the items and work out the price.
- **Stock and payment:** `_reserve_stock`, `_release_all` and `_charge` reserve the stock, charge the customer, and release the stock again on failure.
- **After payment:** `_finalize` commits the stock, redeems the coupon and marks the order paid. `_send_receipt` sends the receipt, and a failure there is still logged and swallowed.

The statements run in the same order as before, with the same exceptions, messages, status changes and log calls. The signature of `process_order` is the same, so callers like `shop/api.py` are unaffected.

The existing tests didn't cover much of the risky logic, so I added `tests/test_checkout_characterization.py` first. It pins:

- invalid quantities
- an invalid coupon
- tax rounded half-up per line
- VIP discount stacking on top of a coupon
- the free-shipping threshold, including exactly 5000
- the default tax rate
- rollback when only some items could be reserved
- the order of reserve, release and commit calls
- coupon redemption only after a successful charge
- the swallowed receipt failure

I did not commit, since you didn't ask for that. I also didn't run the crapper, dryer or mutator tools from the ub-mode skill, because they aren't in the repo.