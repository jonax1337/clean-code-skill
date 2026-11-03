I rewrote `getPrice` in `src/pricing.ts`. The 2 existing tests pass and `npm run typecheck` reports no errors.

- **Signature:** It still takes `(product, isMember, coupon?)` and returns a number, so none of the callers in `cart.ts`, `checkout.ts`, `priceList.ts` or `feeds/export.ts` needed changes.
- **Behavior:** The discount rules are the same. Members get 10% off books and 5% off everything else. The `SAVE10` coupon takes 10 off and never goes below 0. The result is rounded to cents.
- **Structure:** I split it into three small helpers, `applyMemberDiscount`, `applyCoupon` and `roundToCents`, and the exported function now just chains them.
- **Constants:** The magic numbers (`0.9`, `0.95`, `"SAVE10"`, `10`, `100`) are now named constants (G25).
- **Types:** The `any` parameter is now a `PricedProduct` interface with `price: number` and an optional `category` (TS3).
- **Comparisons:** `==` became `===` (G26).

One thing to be aware of: the interface is stricter than `any`. A caller that passes an object without a numeric `price` would now fail typechecking. The typecheck is clean today, so none do.

I didn't add tests for `getPrice` itself. The two existing tests cover it only through the cart.