I cleaned up `getPrice` in `src/pricing.ts`. The 10 tests pass and `tsc --noEmit` reports no errors, so the existing callers still type-check.

**What changed**
- The nested `if`s are now two steps: apply the member rate, then apply the `SAVE10` coupon. Rounding moved into a small `roundToCents` helper.
- The magic numbers (`0.9`, `0.95`, `"SAVE10"`, `10`) are named constants.
- `p: any` is now an exported `Priceable` type (`{ price: number; category?: string }`). It fits every call site: `Product`, the feed rows (no category), and the inline objects in `cart.ts` and `checkout.ts`.
- The function and its parameters are unchanged. I renamed `p` to `product`, which only matters inside the function.

**Tests**
- `src/pricing.ts` had no tests of its own, only two indirect ones in `test/cart.test.ts`. I added `test/pricing.test.ts` with 8 tests and ran them against the original code before refactoring.
- They cover:
  - the member discount for books, other categories and uncategorized products
  - `SAVE10`, including the floor at 0 and ordering after the member discount
  - unknown or empty coupons
  - rounding to cents
- Results: `npm test` shows 10 tests, 10 pass, 0 fail.

**Left alone**
- `cartTotal` calls `getPrice` with a fake `"mixed"` product just to apply the coupon. That works but is awkward. It's outside what you asked for, so I didn't touch it.