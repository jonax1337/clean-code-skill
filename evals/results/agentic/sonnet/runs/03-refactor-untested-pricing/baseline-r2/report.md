I cleaned up `getPrice` in `src/pricing.ts`. I haven't run any tests or the type checker, and I didn't look for a test suite.

- **Named constants:** The magic numbers (`0.9`, `0.95`, `10`) are now constants.
- **Flatter logic:** The nested `if`s are gone. The member discount is a single ternary, and the coupon check is one condition.
- **Floor at zero:** `Math.max(price - SAVE10_AMOUNT, 0)` replaces the separate `if (price < 0)` line.

The signature, the `any` type on `p`, the discount order and the rounding are all unchanged, so the callers in `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts` shouldn't see any difference. I read the logic through and expect identical results. An unknown coupon is still ignored, same as before.

I left `p: any` alone because tightening it could break callers. `feeds/export.ts` passes DB rows, and `cart.ts` and `checkout.ts` pass ad-hoc objects. A typed `{ price: number; category?: string }` would be a reasonable follow-up if you want it.