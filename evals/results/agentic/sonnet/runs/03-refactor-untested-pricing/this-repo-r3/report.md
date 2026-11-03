I cleaned up `getPrice` in `src/pricing.ts`, and its behavior and signature are unchanged for every caller. `npm test` gives 10 passed, 0 failed, and `tsc --noEmit` reports no errors.

**What changed**
- The member rates (0.9 and 0.95) and the `SAVE10` coupon and its amount (10) are now named constants.
- The nested `if` blocks are now two expressions: member discount first, then coupon.
- The category choice sits in `memberFactor`, and the rounding in `roundToCents`.
- `p: any` is now `{ price: number; category?: string }`, and the return type is `number`. I checked this against all four callers: `Product`, the ad-hoc `{ price, category: "mixed" }` in `cart.ts`, the optional category in `checkout.ts`, and the category-less feed rows. The type checker accepts all of them.

**Tests**
`getPrice` had no tests, so I added `test/pricing.test.ts` before refactoring. It has 8 tests covering the book and other-category member rates, `SAVE10` and its floor at zero, unknown and empty coupons, the order of discount and coupon, and rounding. They passed against the original code and still pass.

I left the callers alone.