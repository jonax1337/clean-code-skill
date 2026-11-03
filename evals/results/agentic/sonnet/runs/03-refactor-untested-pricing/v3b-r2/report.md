I refactored `getPrice` in `src/pricing.ts` without changing what it returns. `npm test` shows 9 passed and 0 failed, and `npm run typecheck` reports no errors.

- **Structure:** the nested `if`s are now two small helpers, `applyMemberDiscount` and `applyCoupon`, and `getPrice` just composes them. The discount factors, the `SAVE10` coupon name and its amount are named constants. I also swapped `==` for `===`.
- **Types:** `p: any` is now `{ price: number; category?: string }`. This accepts every call site: `Product`, the ad-hoc objects in `cart.ts` and `checkout.ts`, and the category-less feed rows. The signature is otherwise unchanged, so no callers needed edits.
- **Tests:** `getPrice` had no direct tests, so I added `test/pricing.test.ts` with 7 cases. They cover the book and other-category discounts, a missing category, `SAVE10` with the floor at 0, member discount applied before the coupon, unknown coupons, and rounding. I ran them against the original code first, then again after the refactor.

I accidentally wrote `pricing.ts` to a mistyped directory at one point. I moved it into the repo and deleted the stray directory. `git status` shows only `src/pricing.ts` modified and the new test file.

I left alone the duplicate rounding in `cartTotal`, because it is outside this task. I haven't committed anything.