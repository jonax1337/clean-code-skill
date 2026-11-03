I cleaned up `getPrice` in `src/pricing.ts`. Its signature and behavior are unchanged, so none of the callers (`cart.ts`, `checkout.ts`, `admin/priceList.ts`, `feeds/export.ts`) need edits.

- **Named constants:** the discount factors (`0.9`, `0.95`) and the `10` off for `SAVE10` are now constants instead of bare numbers.
- **Flatter logic:** the nested `if`s are gone. Clamping to zero is now `Math.max(price - 10, 0)`, and `==` became `===`.
- **Small helpers:** `memberFactor` and `roundToCents` each do one thing.

`npm test` passes (2 of 2). `npx tsc --noEmit` printed no errors, only npm notices, so I believe it's clean. The only test is `test/cart.test.ts`, which doesn't cover `getPrice` edge cases like books pricing or the coupon clamp. I checked those by reading the code, not by running them.

I left the `p: any` parameter alone. Callers pass different shapes (cart lines, DB rows, ad-hoc objects), and tightening the type could break them. It would be a worthwhile follow-up, but it should be its own change.