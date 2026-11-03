I cleaned up `getPrice` in `src/pricing.ts`. I didn't run tests or the type checker, so it's unverified beyond reading the code.

- **Constants:** the magic numbers (`0.9`, `0.95`, `10`) are now named constants.
- **Control flow:** the nested `if`s are flattened. The member discount is a single ternary, and the coupon clamp uses `Math.max(price - 10, 0)`.
- **Behavior:** the same discounts apply in the same order, with the same rounding to cents. The signature is unchanged, including `p: any`, so the callers in `cart.ts`, `checkout.ts`, `priceList.ts` and `feeds/export.ts` need no changes. I left `p: any` alone because those callers pass different shapes of object.

One edge case differs slightly: if `p.price` were `NaN`, the old `if (price < 0)` check would leave it as `NaN`, while `Math.max` also returns `NaN`, so the result is the same.