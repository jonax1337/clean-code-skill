I refactored `getPrice` in `src/pricing.ts` without changing its behavior or signature. The 2 existing tests pass and `tsc --noEmit` reports no errors.

- **What changed:** The magic numbers and coupon code are now named constants. The member discount, the coupon and the rounding each have their own small helper. `getPrice` is now two lines that call them in order.
- **Behavior:** `getPrice(p: any, isMember, coupon?)` takes and returns the same values as before. The `SAVE10` clamp at 0 is now `Math.max(0, price - 10)`, which gives the same result. I left `p` typed as `any` on purpose. Narrowing it could break the five call sites (`cart.ts`, `checkout.ts`, `feeds/export.ts`, `admin/priceList.ts`), which pass differently shaped objects.
- **Test coverage:** The tests only cover the cart. Nothing tests `getPrice` directly, for example the book discount or a coupon on a price under 10. I read the new code against the old and they match, but I didn't add tests.

I can add direct `getPrice` tests and then tighten the `any` type if you want.