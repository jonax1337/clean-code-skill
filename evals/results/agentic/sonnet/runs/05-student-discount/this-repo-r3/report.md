I added a `STUDENT` customer type. It gets 10% off, or the loyalty rate if that's higher. I ran `java tools/RunTests.java` and all 16 tests pass.

- **Discount logic:** in `DiscountPolicy.java`, a student gets `max(10%, loyalty rate)`. That means silver loyalty (5%) gives the student 10%, and gold loyalty (15%) gives 15%. The two are never added together.
- **Receipt label:** `ReceiptFormatter.java` has a switch over customer types that needed a new case, so student receipts now read `(student)`.
- **Docs:** I added the student rate and the "never combined" rule to the discount table in `README.md`.
- **Tests:**
  - `DiscountPolicyTest.java` covers a student with no points, with silver points, and with gold points.
  - `ReceiptFormatterTest.java` has a new test for the student label and a 1.00 discount on a 10.00 order.

I added `STUDENT` at the end of the enum so the existing members keep their order.

I haven't committed anything.