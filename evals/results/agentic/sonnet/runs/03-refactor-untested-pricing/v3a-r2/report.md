I cleaned up `getPrice` in `src/pricing.ts` without changing what it returns. The 9 tests and the typecheck pass.

- **Structure:** the nested `if`s are now two lines, a member price and then a coupon price. A small `memberFactor` helper picks the 0.9 (books) or 0.95 (everything else) discount. The discounts and the 10 off for `SAVE10` are named constants.
- **Types:** `p: any` is now a small `{ price: number; category?: string }`, and the return type is `number`. `category` has to be optional because `feeds/export.ts` passes rows that have none. `tsc` accepts every caller, and I didn't change any signatures.
- **Tests:** I added `test/pricing.test.ts` with 7 cases, since `getPrice` had no direct tests. They cover the member discounts, `SAVE10` including the floor at zero, unknown coupons, the order of discount then coupon, and rounding. I stashed the refactor and ran them against the original code, and they passed there too, so they show the behavior is unchanged.

I left alone the `Math.round(... * 100) / 100` rounding that appears in both `getPrice` and `cart.ts`. I also didn't touch `cartTotal`, which calls `getPrice` with a fake `"mixed"` product to apply the cart coupon. That works, but it's an awkward reuse you may want to tidy separately.

I haven't committed anything.