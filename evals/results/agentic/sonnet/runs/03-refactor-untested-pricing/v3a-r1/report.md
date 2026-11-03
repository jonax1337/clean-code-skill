I rewrote `getPrice` in `src/pricing.ts` so it reads top to bottom, and its behavior is the same. `npm test` passes (9 tests, 0 failures) and `npm run typecheck` reports no errors.

- **Structure:** the nested `if`s are gone. `getPrice` now applies the member rate, then the coupon, then rounds. Three small helpers do those steps: `memberRate`, `applyCoupon` and `roundToCents`.
- **Constants:** the magic numbers (`0.9`, `0.95`, `10`, `"SAVE10"`) are named constants.
- **Types:** `p: any` is now a small `Priced` type, `{ price: number; category?: string }`. Callers pass a `Product`, a feed row with no category, and `{ price, category: "mixed" }`. `category` has to stay optional and typed as `string` so all three still compile, and the typecheck confirms they do.
- **Public signature:** the arguments are unchanged. I renamed `p` to `product` and added an explicit `number` return type, which is what it already returned.
- **Tests:** `getPrice` had no direct tests, so I added `test/pricing.test.ts` before touching it. It covers:
  - member and non-member prices;
  - the books rate versus the default rate;
  - a missing category;
  - `SAVE10` and the floor at zero;
  - unknown coupons;
  - the order of member discount then coupon;
  - rounding to cents.

  They passed against the original code too, and they pass after the change.

I didn't touch the callers in `cart.ts`, `checkout.ts`, `priceList.ts` and `feeds/export.ts`. Nothing is committed.