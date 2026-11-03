I refactored `getPrice` in `src/pricing.ts`. The two tests in `npm test` pass, and `tsc --noEmit` printed no errors.

The signature and results are unchanged, so none of the callers need edits. Those are `cart.ts`, `checkout.ts`, `admin/priceList.ts` and `feeds/export.ts`.

- **G25:** The magic numbers (`0.9`, `0.95`, `10`, `100`, `"SAVE10"`) are now named constants.
- **G30 and G34:** The member discount, coupon and rounding are split into `applyMemberDiscount`, `applyCoupon` and `roundToCents`. `getPrice` now just combines them.
- **G28:** The nested `if` blocks are gone. The coupon check is a guard clause, and the "never below 0" rule is `Math.max(price - 10, 0)`.
- **TS3:** `p: any` is now a `Priceable` interface (`price: number`, optional `category`), and the return type is explicit. The old loose `==` is now `===`.
- **N1:** The parameter `p` is now `product`.

I left the `isMember: boolean` parameter alone. It's a flag argument (F3), but changing it would mean editing every caller.

The tests only cover a couple of cases. Because of that, I kept the old behavior exactly. The coupon floor of 0 still applies only when a coupon is used, and any coupon other than `SAVE10` is ignored.