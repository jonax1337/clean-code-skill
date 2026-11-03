I refactored `getPrice` in `src/pricing.ts`. I haven't run any tests or a type check.

- **Same interface:** the signature `getPrice(p: any, isMember, coupon?)` and the return value are unchanged. All five call sites (`cart.ts`, `checkout.ts`, `admin/priceList.ts`, `feeds/export.ts`) need no edits.
- **Named constants:** the magic numbers and the coupon code are now constants (`0.9`, `0.95`, `"SAVE10"`, `10`).
- **Small helpers:** the logic is split into `applyMemberDiscount`, `applyCoupon` and `roundToCents`, so `getPrice` reads as three steps.
- **Same results:** the nested `if`s became a ternary and `Math.max(price - 10, 0)`. They give the same results as before, including for unknown coupons, which still change nothing.

I left `p: any` alone. Tightening it could break callers that pass differently shaped objects, such as the feed `row`. I can type it properly and run `tsc` if you'd like.