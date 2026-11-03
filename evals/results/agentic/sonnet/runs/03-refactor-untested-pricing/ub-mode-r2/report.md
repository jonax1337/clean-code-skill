I cleaned up `getPrice` in `src/pricing.ts` without changing what it returns. The full test suite and `tsc --noEmit` pass, and the change is committed locally as `b5f76ed`. I haven't pushed it.

- **Tests first:** I added `test/pricing.test.ts` to pin the existing behavior before touching the code. It covers the member discounts, the `SAVE10` coupon (including the floor at 0), unknown coupons, and rounding. All 7 tests passed before and after the refactor.
- **Refactor:** `getPrice` now delegates to two small helpers, `applyMemberDiscount` and `applyCoupon`. The magic numbers are named constants, and the nested ifs are gone. The signature is the same.
- **Type change:** the `p: any` parameter is now `{ price: number; category?: string }`. All five call sites still typecheck.

**Log:**
1. Read `pricing.ts` and grepped for callers (`cart`, `checkout`, `priceList`, `feeds/export`).
2. Wrote the pinning tests and ran them against the old code.
3. Rewrote `getPrice`, then re-ran the tests and the typecheck.
4. Committed.

**Not done:** The skill's crapper, dryer and mutator tools aren't available here, so I didn't run them. A function this small seemed well under the complexity threshold anyway.