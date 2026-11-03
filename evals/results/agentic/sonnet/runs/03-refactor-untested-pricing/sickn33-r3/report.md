I refactored `getPrice` in `src/pricing.ts`. I haven't run any tests or a type-check, and I didn't look for a test suite. I did check the call sites in `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts`.

- **Same interface:** the signature, `any` parameter type and `==` comparisons are unchanged. A tighter type could break callers I haven't seen the types of, such as the `row` in `feeds/export.ts`.
- **Same arithmetic:**
  - Members get 10% off books and 5% off everything else.
  - The `SAVE10` coupon takes 10 off and floors the result at 0.
  - The result is rounded to cents.
  - I wrote the clamp as `Math.max(price - 10, 0)` instead of the old `if (price < 0)`. The two give the same result.
- **Readability:**
  - The magic numbers and the coupon code are now named constants.
  - `getPrice` now reads as three steps: member discount, coupon, rounding. Each step is its own small function (`applyMemberDiscount`, `applyCoupon`, `roundToCents`).
  - The nested `if` blocks are gone.