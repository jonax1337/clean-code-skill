I added the `STUDENT` customer type. Students get 10% off, or their loyalty rate if that's higher. All 15 tests pass, including three new ones.

- **Discount logic:** in `DiscountPolicy.java`, a student gets whichever is bigger of 10% and their loyalty rate. With 500–1999 points (5%) they keep 10%. With 2000 or more points (15%) they get 15%.
- **Enum and receipt:** `STUDENT` is added to `CustomerType`, and the receipt label for it reads "student".
- **Tests:** the new cases in `DiscountPolicyTest` cover a student with no points, with silver points and with gold points.
- **README:** the discount table now has a Student row, plus a line saying discounts aren't combined.