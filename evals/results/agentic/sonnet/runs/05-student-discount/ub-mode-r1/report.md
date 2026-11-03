I added a `STUDENT` customer type. A student gets 10%, or their loyalty rate if that's higher, never both added together. All 14 tests pass, including two new ones for students.

- **Discount rule:** in `DiscountPolicy.rateFor`, a student's rate is the larger of 10% and the loyalty rate for their points. A student with 500 points gets 10%, and one with 2000 points gets the 15% gold rate.
- **Receipt:** `ReceiptFormatter` now labels these customers "student".
- **README:** the discount table now lists students, with a note that discounts don't combine.
- **Commit:** it's committed on `main`. There's no git remote configured, so nothing was pushed.

I wrote the tests and the code in one pass, so I never saw the new tests fail before the change. I also didn't run the crapper, dryer or mutator tools the skill calls for.

Git warned that CRLF line endings will become LF in the files I touched.