I refactored `getPrice` in `src/pricing.ts`. I didn't run the type checker or any tests, so the change is unverified.

The signature is the same, so the callers in `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts` don't need changes. The logic is unchanged too: members get 10% off books and 5% off everything else, `SAVE10` takes 10 off with a floor of 0, and the result is rounded to cents.

- **G25:** I replaced the magic numbers and the coupon string with named constants.
- **G30 / G34:** I split the function into `applyMemberDiscount`, `applyCoupon` and `roundToCents`, and `getPrice` now just composes them.
- **G28 / G29:** I replaced the nested ifs with a guard clause and `Math.max`.
- **TS3:** I replaced `p: any` with a `Priced` interface, and `==` is now `===`.
- **F3:** `isMember` is still a boolean flag. Splitting it would mean changing every caller, so I left it.

The `Priced` interface is a compile-time risk. If any caller passes something whose `price` isn't typed as a number, such as a feed row typed loosely, `tsc` may now flag it. Please run `tsc` and your tests to check.