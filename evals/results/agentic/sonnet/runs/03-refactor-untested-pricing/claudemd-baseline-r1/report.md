I cleaned up `getPrice` in `src/pricing.ts`. The tests (7 of 7) and `tsc --noEmit` both pass, and I ran both after the last edit.

- **Behavior:** The signature and the results are unchanged. That includes the member discounts (10% off books, 5% off everything else), the `SAVE10` coupon flooring at 0, and rounding to cents.
- **What changed:**
  - The discount rates and the coupon amount are now named constants.
  - The nested `if` blocks are flattened.
  - The 5%/10% choice is a ternary.
  - The floor at 0 uses `Math.max`.
- **Callers:** I didn't touch any of them (`cart.ts`, `checkout.ts`, `priceList.ts`, `feeds/export.ts`). I left the `p: any` parameter alone because some callers pass raw rows.
- **New tests:** `test/pricing.test.ts` has five tests, since `getPrice` had none of its own. They cover member and non-member prices, the coupon floor, an unknown coupon, a member plus coupon, and rounding. They pass against the new code, but I didn't run them against the old version.