I split `process_order` in `shop/checkout.py` into small helpers, and its behavior is unchanged as far as the tests can show. All 16 tests pass, the 9 existing ones plus 7 new ones, and the 7 new ones also passed against the old code.

`process_order` now just runs these steps in order:
- `_validate_items`
- `_price_order`, which uses `_subtotal_and_tax`, `_discount` and `_shipping`
- `_reserve_stock`
- `_charge`
- `_finalize`
- `_send_receipt`

The order of side effects and error checks is the same. Exceptions, messages, status values and logging are the same too.

**Log of what I did**
1. I read `checkout.py` and its tests. The existing tests left several branches unpinned: VIP discount, free shipping, invalid quantity, unknown coupon, per-line tax rounding, rollback after a partial reservation, and a receipt-send failure.
2. I added tests for those branches and ran them on the untouched code, where they passed. That is commit `c5ee589`.
3. I did the refactor and re-ran the tests, which still passed. That is commit `5903fdc`.

**What I didn't do**
- **Not pushed:** the two commits are local only. I held off because this is production code, so tell me if you want them pushed to `main`.
- **Duplicate release loop:** the stock-release loop that appeared twice is now one `_release` helper. I didn't change anything else.
- **Skipped tools:** I didn't run the crapper, dryer or mutator tools from the skill. I didn't find them in this environment, so the function sizes weren't measured with them.