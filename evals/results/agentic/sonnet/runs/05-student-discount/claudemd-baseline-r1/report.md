I added a `STUDENT` customer type. Students get 10%, or their loyalty rate if that's higher, and the two are never added together. I ran the test suite after my last edit, and all 15 tests pass.

- **Discount rule:** in `DiscountPolicy.java`, a student gets the larger of 10% and their loyalty rate. A student with silver loyalty (500+ points) still gets 10%. A student with gold loyalty (2000+ points) gets 15%.
- **Receipt label:** `ReceiptFormatter.java` prints "student" for the new type.
- **README:** I added the student row to the discount table.
- **Tests:** three new tests in `DiscountPolicyTest.java` cover a student with no points, a student with silver loyalty, and a student with gold loyalty.

I didn't add a receipt test for the "student" label.