I cleaned up `getPrice` in `src/pricing.ts`. I didn't run tests or a type check, so it's only checked by reading.

- **Magic numbers:** the member discounts (`0.9` for books, `0.95` otherwise) and the `SAVE10` amount are now named constants.
- **Nesting:** the nested `if`s are flattened into a ternary for the member discount and a single `SAVE10` check.
- **Clamping:** `Math.max(price - SAVE10_AMOUNT, 0)` replaces the separate `if (price < 0)` clamp.

I kept the signature, including `p: any`, and the rounding exactly as they were, so behavior is unchanged. That covers every caller I found: `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts`. I left the loose `==` comparisons as they were, since switching to `===` could change behavior for odd inputs.

Tightening `p: any` to a real product type would be a good follow-up. The callers pass a few different object shapes, so I didn't want to risk breaking them here.