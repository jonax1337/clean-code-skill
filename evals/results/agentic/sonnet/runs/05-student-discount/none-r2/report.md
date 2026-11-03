I added a `STUDENT` customer type that gets 10% off. A student who is also a loyalty member gets whichever is bigger, 10% or their loyalty rate, never both added together. All 14 tests pass, including two new ones for students.

In practice, a student gets 10% below 2000 loyalty points and 15% at 2000 or more. The 5% silver tier never wins, because 10% beats it.

- **Discount rule:** `DiscountPolicy.java` has the new case, which takes the larger of 10% and the loyalty rate.
- **Receipt:** `ReceiptFormatter.java` labels these customers "student".
- **Docs:** I added a Student row to the discount table in `README.md`.
- **Tests:** `DiscountPolicyTest.java` now checks a student at 0 and 500 points (10%) and at 2000 points (15%).

Employees still get a flat 20%.

I haven't committed anything.