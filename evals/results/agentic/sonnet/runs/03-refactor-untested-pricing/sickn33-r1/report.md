I refactored `getPrice` in `src/pricing.ts`. I haven't run tests or a type-check, so it's unverified.

- **Signature unchanged:** it still takes `product: any`, `isMember` and an optional `coupon`, and the five callers (`cart.ts`, `checkout.ts`, `admin/priceList.ts`, `feeds/export.ts`) need no changes.
- **Same logic:** the member discount is still 10% off for books and 5% off for everything else. The `SAVE10` coupon still takes 10 off and floors the price at 0. Any other coupon is still ignored, and the result is still rounded to cents.
- **What changed:** the magic numbers are now named constants, and `getPrice` calls three small helpers, `applyMemberDiscount`, `applyCoupon` and `roundToCents`. The nested `if`s are gone.

I left `product` as `any` on purpose. Callers pass different shapes (plain objects, DB rows), and tightening the type could break compilation somewhere I haven't checked.