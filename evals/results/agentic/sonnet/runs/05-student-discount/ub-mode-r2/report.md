I added the `STUDENT` customer type. Students get 10%, or their loyalty rate if that's higher, never both. All 14 tests pass, and the change is committed on `main`. The push didn't go through because the repo has no remote or upstream branch configured, so the commit is local only.

- **Discount rule:** In `DiscountPolicy`, a student's rate is the larger of 10% and their loyalty rate. A student with gold loyalty (2000+ points) gets 15%. One with silver loyalty (500+ points) still gets 10%.
- **Tests:** I added two cases to `DiscountPolicyTest`: students get 10%, and a gold-loyalty student gets 15% rather than the two combined. Before the change the code didn't compile, because the `switch` over customer types didn't cover `STUDENT`. After it, everything passes.
- **Receipt and README:** The receipt now labels these customers "student", and the README discount table has a student row.

Git warned that the line endings (CRLF) in four of the changed files will be converted to LF the next time Git touches them.

**Log:**
1. Read the pricing code and tests.
2. Wrote the tests and added the enum value.
3. Saw the build fail on the non-exhaustive `switch`.
4. Implemented the rate in `DiscountPolicy` and the receipt label.
5. Updated the README table and re-ran the tests.
6. Committed. The push failed because there's no remote.

I didn't run the crapper, dryer or mutator tools. The change is one switch case plus tests.