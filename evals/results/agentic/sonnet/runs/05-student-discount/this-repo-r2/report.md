I added a `STUDENT` customer type with a 10% discount. A student who is also a loyalty member gets the higher of 10% and their loyalty rate, not both. All 16 tests pass (`java tools/RunTests.java`).

- **Discount rule:** in `DiscountPolicy.rateFor`, a student gets the larger of 10% and the loyalty rate. So silver (5%) gives 10%, and gold (15%) gives 15%.
- **Receipt:** `ReceiptFormatter` now labels these customers "student". The switch there had no default, so it would not have compiled without that case.
- **Enum:** `STUDENT` goes at the end of `CustomerType`, so the existing members keep their order.
- **README:** the discount table has a Student row and a note that the two discounts aren't combined.
- **Tests:** I added tests for students with no loyalty points, with silver loyalty and with gold loyalty. I also added a receipt test for the student label and discount amount.