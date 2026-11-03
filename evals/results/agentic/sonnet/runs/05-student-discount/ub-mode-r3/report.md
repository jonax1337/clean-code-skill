I've added the `STUDENT` customer type and committed it on `main`. All 14 tests pass, including two new ones for the student rules. There's no remote configured, so nothing was pushed.

- **Discount rule:** a student gets 10%, or their loyalty rate if that's higher. A student with 2000+ points gets 15%, and one with 500 points still gets 10%. The rule is in `DiscountPolicy.java`.
- **Receipt label:** the exhaustive switch in `ReceiptFormatter` no longer compiled with the new enum value, so I added a "student" label.
- **README:** the discount table now lists students, with a note that the two discounts aren't combined.

**Action log**
1. Added the two failing test cases in `DiscountPolicyTest`.
2. Added `STUDENT` to `CustomerType` and the rule to `DiscountPolicy`.
3. Fixed the compile error in `ReceiptFormatter` and updated the README.
4. Ran the tests, then committed.

I didn't run the crapper, dryer or mutator tools, since none are in the repo.