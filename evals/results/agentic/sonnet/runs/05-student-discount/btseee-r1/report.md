I added a `STUDENT` customer type that gets 10% off. A student who is also a loyalty member gets whichever is bigger, the student rate or their loyalty rate, never both. All 14 tests pass, including two new ones.

- **Discount rule:** In `DiscountPolicy.java`, `STUDENT` gets 10%, or the loyalty rate if that's higher. So a student with 500 points gets 10% (silver is only 5%). A student with 2000 points gets 15% (gold).
- **Receipt:** I added a "student" label in `ReceiptFormatter.java`, since its switch needs every customer type covered.
- **Docs:** `README.md` now lists the student rate and the "bigger of the two" rule.
- **Tests:** The new tests in `DiscountPolicyTest.java` cover a student with no points, a student with silver-level points, and a student with gold-level points.

I haven't committed anything.