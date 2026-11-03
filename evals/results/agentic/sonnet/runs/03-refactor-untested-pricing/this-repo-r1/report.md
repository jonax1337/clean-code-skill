I cleaned up `getPrice` in `src/pricing.ts` and its behavior is unchanged. `npm test` passes (11 of 11) and `npm run typecheck` reports no errors.

**What changed in `src/pricing.ts`:**
- The nested `if`/`else` blocks are now two short steps: apply the member rate, then the coupon.
- The member rates (0.9 for books, 0.95 otherwise) and the `SAVE10` coupon code and amount are now named constants.
- The member rate and the cent rounding each moved into a small helper.
- `p: any` became a narrow `{ price: number; category?: string }`. This matches how every caller uses it: products, the ad-hoc objects in `cart.ts` and `checkout.ts`, and feed rows with no category. The typecheck confirms all callers still fit.
- I kept the same order of operations: member discount, then coupon, then round. The floor at zero is unchanged.

**Tests:** `getPrice` had no tests of its own, so I added `test/pricing.test.ts` first and ran it against the original code. It covers:
- the member rates, including an item with no category
- the coupon, including the floor at zero and its order after the member discount
- unknown and empty coupons
- rounding

**One difference:** the original used loose equality (`==`) on the category and coupon. I switched to strict equality (`===`). The only inputs where that could matter are non-string values, which the types already rule out for callers.

I didn't change any callers or the public signature. I haven't committed anything.