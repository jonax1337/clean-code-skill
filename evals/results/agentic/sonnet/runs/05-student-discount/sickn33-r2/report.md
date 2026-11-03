I added a `STUDENT` customer type. Students get 10% off, or their loyalty rate if that's higher. All 15 tests pass, including three new ones.

- **Discount rule:** in `DiscountPolicy`, a student's rate is the larger of 10% and their loyalty rate. A student with 500 or more points (5%) gets 10%. A student with 2000 or more points (15%) gets 15%. The two are never added together.
- **Receipt label:** `ReceiptFormatter` now prints "student" for the new type.
- **Docs:** the README discount table lists the student rate and says discounts aren't combined.
- **New tests:** a student with no points, one with silver loyalty and one with gold loyalty.

I haven't committed anything.