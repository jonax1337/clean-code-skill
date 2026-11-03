I added a `STUDENT` customer type. Students get 10% off, or their loyalty rate if that's higher, never both. All 14 tests pass, including the new ones.

- **Discount rule:** in `DiscountPolicy.java`, a student gets the larger of 10% and their loyalty rate. With 500–1999 points (5%) they still get 10%. With 2000 or more points (15%) they get 15%.
- **Receipt:** `ReceiptFormatter.java` labels these customers "student". This was needed because the switch over customer types wouldn't compile without it.
- **Tests:** two new cases in `DiscountPolicyTest.java` cover a plain student and a student with loyalty points.
- **Docs:** the discount table in `README.md` now has a Student row.