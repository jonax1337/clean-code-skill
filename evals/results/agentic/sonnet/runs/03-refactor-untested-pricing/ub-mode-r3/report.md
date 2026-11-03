I cleaned up `getPrice` in `src/pricing.ts` and its behavior is unchanged. All 10 tests pass (2 existing, 8 new) and `tsc` is clean. I committed it locally as `831fabe` and haven't pushed.

**What I did, and why**
1. **Pinned the old behavior first.** I added `test/pricing.test.ts` with 8 tests and ran them against the old code, where they passed. They cover:
   - the member discount (10% off books, 5% off everything else),
   - `SAVE10` and its floor at 0,
   - an unknown coupon being ignored,
   - the member discount applying before the coupon,
   - rounding to cents.
2. **Refactored.** The nested `if`s are now two small helpers, `applyMemberDiscount` and `applyCoupon`. The magic numbers are named constants, and `getPrice` just combines the two and rounds. The `p: any` parameter now has a real type, `{ price: number; category?: string }`. `category` is optional because `checkout.ts` and `feeds/export.ts` can pass rows without one. The old code treated a missing category as non-books, and so does the new code.
3. **Checked the callers.** `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts` call `getPrice` unchanged. The first typed version broke `tsc` in two of them, which is why `category` became optional.

One difference: the old code used `==`, so it also accepted loosely equal values. The new code uses `===`. For the string inputs the callers pass, nothing changes.

I didn't run the crapper, dryer or mutator tools. The function is now small enough that I didn't think they'd tell us anything.