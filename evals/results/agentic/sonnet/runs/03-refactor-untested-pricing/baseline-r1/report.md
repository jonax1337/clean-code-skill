I cleaned up `getPrice` in `src/pricing.ts`. I haven't run any tests or the type checker, so the "nothing breaks" claim rests on reading the code.

- **Constants:** the discount rates (`0.9`, `0.95`) and the coupon amount (`10`) are now named constants.
- **Rounding:** it lives in a small `roundToCents` helper.
- **Conditionals:** the nested `if`s are flattened, and the `price < 0` clamp became `Math.max(price - SAVE10_AMOUNT, 0)`.

I kept the signature, the loose `p: any` type and the `==` comparisons exactly as they were, so the callers in `cart.ts`, `checkout.ts`, `feeds/export.ts` and `admin/priceList.ts` need no changes. The output should be the same for every input. A coupon is still only applied when it equals `"SAVE10"`, and the result is still floored at 0 and rounded to cents.

I left `p: any` alone on purpose. Tightening it could break callers that pass partial objects, like the `{ price, category }` literals in the cart and checkout code. I can add a proper `Product` type if you want.