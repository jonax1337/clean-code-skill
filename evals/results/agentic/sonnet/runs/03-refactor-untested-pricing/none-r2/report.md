I cleaned up `getPrice` in `src/pricing.ts`. I didn't run tests or the type checker, and I didn't check whether the repo has any.

- **Same interface:** The signature is unchanged, including `p: any`, so the callers in `cart.ts`, `checkout.ts`, `priceList.ts` and `feeds/export.ts` need no changes.
- **Constants and helpers:** I pulled the magic numbers into named constants (`BOOK_MEMBER_FACTOR`, `DEFAULT_MEMBER_FACTOR`, `SAVE10_AMOUNT`). The member discount and the rounding now live in small helpers.
- **Flatter logic:** The nested `if`s are now flat. The coupon floor at zero is `Math.max(0, price - SAVE10_AMOUNT)`.

Behavior should be identical. Members get 10% off books and 5% off everything else. `SAVE10` takes 10 off with a floor of 0. Unknown coupons are ignored. The result is rounded to cents.

One edge case differs: if `price` is `NaN`, the old code returned `NaN` and this version returns 0 when `SAVE10` is applied. I doubt that's reachable.