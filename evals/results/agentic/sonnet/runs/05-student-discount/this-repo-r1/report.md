I added a `STUDENT` customer type that gets 10% off. A student who is also a loyalty member gets whichever is larger, their 10% or their loyalty rate. The test run (`java tools/RunTests.java`) shows 16 tests found, 16 successful, 0 failed.

- **Discount rule:** In `DiscountPolicy`, a student's rate is the larger of 10% and the loyalty rate (`STUDENT_RATE.max(loyaltyRateFor(...))`). A student with silver loyalty (500+ points, 5%) gets 10%. A student with gold loyalty (2000+ points, 15%) gets 15%.
- **Receipt label:** `ReceiptFormatter` had its own switch on customer type, so I added a "student" label there. Without it the code would not have compiled.
- **Enum order:** I put `STUDENT` last in `CustomerType` so the existing order stays the same.
- **Tests:** I added three discount tests (10% with no points, silver loyalty keeps 10%, gold loyalty gets 15%) and one receipt test for the label and the discount line.
- **Docs:** I updated the discount table in the README and added a line saying discounts aren't combined.

I didn't add any check that a customer is really a student. The type is simply set on the `Customer`.