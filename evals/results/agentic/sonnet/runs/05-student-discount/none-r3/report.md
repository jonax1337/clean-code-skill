I added a `STUDENT` customer type. Students get 10%, or their loyalty rate if that's higher (so 15% at 2000 or more points). I haven't compiled it or run the tests, so none of this is verified yet.

- **Enum:** `CustomerType.java` now has `STUDENT`.
- **Discount rule:** `DiscountPolicy.rateFor` returns the larger of 10% and the loyalty rate for students. Silver loyalty (5%) loses to 10%, and gold (15%) wins.
- **Tests:** `DiscountPolicyTest` has two new cases. One checks a student with no points gets 10%. The other checks a student at 500 points gets 10% and at 2000 points gets 15%.
- **README:** the discount table and a short note on the no-stacking rule are updated.

The library has no build tool, and running the tests needs the JUnit jar in `lib/`. To run them, use `java tools/RunTests.java`.