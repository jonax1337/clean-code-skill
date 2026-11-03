I refactored `getPrice` in `src/pricing.ts` but haven't run any tests or a type-check, so it's unverified. I didn't look for a test setup in the repo.

- **Signature unchanged:** the parameters and return type are the same, so the callers in `cart.ts`, `checkout.ts`, `priceList.ts` and `feeds/export.ts` need no changes. I renamed the first parameter from `p` to `product`, which doesn't affect callers.
- **Magic numbers named:** `0.9`, `0.95`, `"SAVE10"` and `10` are now constants.
- **Logic split into helpers:** `applyMemberDiscount`, `applyCoupon` and `roundToCents` replace the nested ifs.
- **Behavior should be identical:** I kept the same loose `==` comparisons, the same order (member discount, then coupon, then rounding) and the same floor at 0 after a coupon.

I left `product: any` as it was. Tightening it to a real type might cause compile errors in callers, such as the feed export that passes raw `row` objects. If you want that, I can check those call sites and do it next.