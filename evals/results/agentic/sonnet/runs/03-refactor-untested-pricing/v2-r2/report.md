I cleaned up `getPrice` in `src/pricing.ts`. The 2 existing tests pass and `tsc --noEmit` is clean.

- **Signature unchanged:** it is still `getPrice(p: any, isMember, coupon?)`, so the callers in `cart.ts`, `checkout.ts`, `priceList.ts` and `feeds/export.ts` are untouched.
- **Magic numbers:** the discount values (0.9, 0.95, `"SAVE10"`, 10) are now named constants (G25).
- **Nesting:** the nested `if`s are flattened.
- **Helpers:** `memberFactor` and `roundToCents` are small helpers.
- **Coupon clamp:** `Math.max(0, …)` replaces the manual "if below zero, set to zero" check.
- **Comparison:** the comparisons use `===` instead of `==`. The only difference is a non-string `category` or `coupon`, such as a `String` object, which would no longer match.

I left `p: any` alone. Typing it properly is a good follow-up, but it could surface type errors in callers such as the `row` in `feeds/export.ts`. The tests only cover cart and checkout totals, not `priceList.ts` or `feeds/export.ts`.