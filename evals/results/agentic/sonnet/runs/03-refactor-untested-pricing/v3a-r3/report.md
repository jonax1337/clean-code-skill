I cleaned up `getPrice` in `src/pricing.ts` without changing what it returns. All 9 tests pass and `tsc --noEmit` reports no errors.

**What changed**
- The nested `if`s are now two straight steps. The member discount applies first, then the `SAVE10` coupon, then the result is rounded to cents.
- Two small private helpers, `memberRate` and `roundToCents`, hold the category rate and the rounding.
- The magic numbers are named constants: `BOOK_MEMBER_RATE`, `DEFAULT_MEMBER_RATE`, `SAVE10_COUPON` and `SAVE10_AMOUNT`.
- The `any` parameter is replaced by an exported `Priceable` type, `{ price: number; category?: string }`. It covers every caller: `Product`, the `{ category: "mixed" }` object in `cart.ts`, and `FeedRow`, which has no category.
- `==` is now `===`, and the function has an explicit `number` return type.
- The function name and parameter order are the same, so no caller needed edits.

**Tests**
`getPrice` had no tests, so I added `test/pricing.test.ts`. It covers non-members, the book and other-category member rates, a missing category, `SAVE10` including the floor at 0, member discount before coupon, ignored coupons, and rounding. I wrote the tests after the refactor, then ran them against the original `getPrice` with `git stash`. All 9 passed there too, so the behavior matches, including the odd cases.

I left the rest of the codebase alone. `cart.ts` rounds again after calling `getPrice`, and it passes a fake `{ category: "mixed" }` product to apply the cart coupon. That works but is awkward, so it could be a follow-up.