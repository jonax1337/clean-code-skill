I rewrote `getPrice` in `src/pricing.ts` without changing what it returns. The 8 tests pass (the 2 existing ones plus 6 new ones), and `tsc --noEmit` reports no errors.

- **Names:** the magic numbers and the coupon code are now named constants, and the parameter `p` is now `product`.
- **Structure:** the nested `if`s are flattened, and the member-discount lookup and cent rounding are small helpers. The `price < 0` clamp became `Math.max(…, 0)`.
- **Types:** `p: any` is now a small `Priceable` type (`price: number`, optional `category?: string`) with an explicit `number` return. All four callers (`cart.ts`, `checkout.ts`, `feeds/export.ts`, `admin/priceList.ts`) type-check unchanged, so the signature is call-compatible.
- **Arithmetic:** discounts are now applied as `1 - rate` rather than a literal multiplier. In JS, `1 - 0.1` and `1 - 0.05` equal `0.9` and `0.95` exactly, so the results are identical. I checked this by reasoning and by the rounding tests, not by comparing the old and new function over many inputs.

I added `test/pricing.test.ts` before changing the code and ran it against the original, since `getPrice` had no direct tests. It covers:
- the member discounts (books, other categories, no category);
- `SAVE10`, including the floor at zero;
- unknown and empty coupons;
- discount-before-coupon ordering;
- rounding to cents.

I left the callers alone. In `cart.ts`, `cartTotal` calls `getPrice` with a fake `"mixed"` product to apply the cart coupon. That works, but a dedicated `applyCoupon` function would be clearer. It's a separate change, so I didn't make it.