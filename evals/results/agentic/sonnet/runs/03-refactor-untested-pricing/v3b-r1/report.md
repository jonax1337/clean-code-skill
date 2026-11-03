I rewrote `getPrice` in `src/pricing.ts` so it reads more clearly, and its behavior is unchanged. `npm test` passes (11 tests, 0 failures) and `npm run typecheck` reports no errors.

**What changed**
- The member discount and the coupon are now two small helpers, `applyMemberDiscount` and `applyCoupon`. `getPrice` calls them in order and then rounds.
- The numbers `0.9`, `0.95`, `"SAVE10"` and `10` are now named constants.
- The nested `if` blocks are gone.
- The `any` parameter is now `Priced`, which is `{ price: number; category?: string }`. `category` is optional because `feeds/export.ts` passes rows that have none. The signature accepts the same call shapes as before, and the typecheck confirms that all five callers still compile.

**Tests**
`getPrice` had no tests, so I added `test/pricing.test.ts` with 9 tests and ran them against the original code first. They cover:
- the book and non-book member discounts, and a product with no category
- `SAVE10`, including the floor at zero
- unknown, empty and lowercase coupons being ignored
- the member discount applying before the coupon
- rounding to cents

**Left alone**
- The callers. Their `"mixed"` category and the way `cart.ts` reuses `getPrice` to apply the cart coupon work as before, and I didn't touch them.
- I also kept the `Math.round(x * 100) / 100` rounding, since changing it could shift some prices by a cent.

Nothing is committed.