I cleaned up `getPrice` in `src/pricing.ts`. I didn't run tests or the type checker.

- **Constants:** the magic numbers are now named: `MEMBER_DISCOUNT_BOOKS`, `MEMBER_DISCOUNT_DEFAULT` and `SAVE10_AMOUNT`.
- **Flatter logic:** the nested `if`s are gone. The member discount is a single ternary, and the coupon check is one `if`.
- **Clamping:** the coupon clamp is now `Math.max(price - SAVE10_AMOUNT, 0)`.

The signature, the `==` comparisons, the `any` parameter type and the rounding are unchanged. The callers in `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts` should behave exactly as before. The `p: any` type is still loose. Tightening it would touch the callers, so I left it.