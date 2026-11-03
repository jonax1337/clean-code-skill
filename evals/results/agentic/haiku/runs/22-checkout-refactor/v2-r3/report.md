`process_order` in `shop/checkout.py` is now a short sequence of steps, and its behavior is unchanged. The existing 9 tests pass, and an equivalence check I wrote found no differences.

**What changed**

`process_order` now reads as:

1. `_check_items`: validate the order
2. `_total_cents`: price it (subtotal, tax, discount, shipping)
3. `_reserve_stock`: reserve each item
4. `gateway.charge`, with the decline path handled inline
5. `_complete_payment`: commit stock, redeem the coupon, mark the order paid
6. `_send_receipt`: notify, logging but not raising on failure

The two identical release loops (out of stock and payment declined) became one `_abandon` helper. Pricing is split into `_subtotal_and_tax`, `_discount_cents`, and `_shipping_cents`. The per-line tax rounding comment moved with its code.

Public names, signatures, the constants, and `refund_order` are unchanged, and `api.py` needs no changes. The file is still modified in the working tree and not committed.

**How I checked behavior**

- Existing tests: 9/9 pass before and after.
- Equivalence check: I ran the original (from `git show HEAD`) and the new code on 20,000 random scenarios. I compared the return value, exception type, message and cause, order fields, the inventory log, gateway charges, notifier calls, and coupon state. There were 0 mismatches. The scenarios covered VIP, several countries, coupons, invalid quantities, out-of-stock, declined payments, unexpected gateway errors, and notifier failures.
- The harness lives in `C:\Users\Jonas\AppData\Local\Temp\cc-charness`, outside the repo.

**Caveats**

- The random run had 880 successful orders, 464 unexpected gateway errors, and the rest rejected. Declined payments and out-of-stock are in there too, but they're mostly counted under the generic rejection type.
- No linter is installed here, so I didn't lint the file.

If you want the behavior pinned permanently, a few regression tests for VIP discounts, free shipping, and multi-item release on decline would be a useful follow-up. I didn't add them since you asked only for the refactor.