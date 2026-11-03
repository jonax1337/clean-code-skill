I split `process_order` in `shop/checkout.py` into small helpers, and behavior is unchanged. All 16 tests pass, including 7 I wrote and ran against the old code first. I committed locally. There's no git remote configured, so nothing was pushed.

**What `process_order` looks like now**

It reads as a short sequence of steps:
1. `_validate_items`
2. `_total_cents`, which uses `_subtotal_and_tax` and `_discount`
3. `_reserve_all`
4. `_charge`
5. `_finalize`
6. `_send_receipt`

I kept the ordering, exception types, messages, status changes and logging exactly as they were. The per-line tax rounding comment moved with the code it explains. I also added a small `_release` helper for the stock-release loop that appeared twice.

**What I did first**

The existing tests missed several branches. I added 7 tests for these:
- VIP discount applied after a coupon
- Free shipping at 5000 cents after discount
- Invalid coupon
- Non-positive quantity
- Partial reservation rollback on out-of-stock
- Receipt send failure
- Per-line tax rounding

**Commits**
- `e439716` adds the tests.
- `09aef37` is the refactor.

**Not done**

The skill also asks for the crapper, dryer and mutator tools, and I didn't run them. They aren't available in this environment, so I haven't measured complexity or mutation coverage. Each helper is short, but treat that as unverified.

Git warned that `shop/checkout.py` has CRLF line endings that will be normalized to LF. Check that this matches your repo's line-ending settings.