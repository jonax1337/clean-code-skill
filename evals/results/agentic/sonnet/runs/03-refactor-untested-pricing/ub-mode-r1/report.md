I cleaned up `getPrice` in `src/pricing.ts` and committed it as `39b8fb1` on `main`. I haven't pushed it. Its behavior is unchanged: all 8 tests pass and the typecheck is clean.

- **Safety net:** `getPrice` had no tests, so I first wrote `test/pricing.test.ts` and ran it against the old code. It covers:
  - the member discounts (10% on books, 5% on everything else);
  - the `SAVE10` coupon, including the floor at 0;
  - unknown coupons being ignored;
  - the member discount being applied before the coupon;
  - rounding to cents.
- **Refactor:** I flattened the nested `if`s, replaced the magic numbers with named constants, and used `Math.max` for the floor at 0.
- **Callers:** The signature is the same (`p: any, isMember, coupon?`), so nothing that calls it needed to change. That covers `cart.ts`, `checkout.ts`, `feeds/export.ts` and `admin/priceList.ts`.
- **Left alone:** The `any` type on `p` is still there. Tightening it to `Product` would be a good follow-up, but it could ripple into the callers, so I didn't do it here.
- **Push:** I held off because you didn't ask for one. Say the word and I'll push to `main`.

I skipped the crapper, dryer and mutator tools. None of them are in the repo, and the function is small enough that they wouldn't change anything.