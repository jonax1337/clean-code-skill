I refactored `getPrice` in `src/pricing.ts`. I didn't run tests or a type-check, so it's untested.

- **Same interface:** the signature and return value are unchanged, so the callers in `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts` need no edits. I also kept `p: any` so callers that pass loosely typed objects still compile.
- **Structure:** the nested `if`s are now three small helpers: `applyMemberDiscount`, `applyCoupon` and `roundToCents`. `getPrice` reads as member discount, then coupon, then rounding.
- **Constants:** the magic numbers (`0.9`, `0.95`, `10`) are now named constants.
- **Behavior:**
  - Books get 10% off for members and everything else gets 5%.
  - `SAVE10` takes 10 off and the price never goes below 0.
  - Unknown coupons are ignored.
  - The result is rounded to cents.
  - Bad input behaves as before: a `NaN` price still gives `NaN`.