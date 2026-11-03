I cleaned up `getPrice` in `src/pricing.ts`. The tests pass (2 of 2) and `tsc --noEmit` reports no errors.

- **Signature:** it is unchanged, including `p: any`, so none of the callers in `cart.ts`, `checkout.ts`, `priceList.ts` and `feeds/export.ts` need edits.
- **Constants:** the member factors (0.9 for books, 0.95 otherwise), the `"SAVE10"` coupon code and its 10 discount are now named constants.
- **Helpers:** the member factor and the cent rounding are small private functions, `memberFactor` and `roundToCents`.
- **Simplified code:** the nested `if`s are gone. The clamp at zero is now `Math.max(price - 10, 0)`.
- **Behavior:** the arithmetic runs in the same order, so results are identical. The one deliberate difference is that `==` became `===`. This only matters if a caller passes a non-string category or coupon, which I didn't find.

The existing tests only cover the cart. They don't test `getPrice` directly, for example the books rate or the zero clamp. I didn't add any, since you asked for a cleanup.

Typing `p` as `{ price: number; category?: string }` would be a good follow-up. I left it out because it could cause type errors in callers such as the feed export, which passes a row of unknown shape.