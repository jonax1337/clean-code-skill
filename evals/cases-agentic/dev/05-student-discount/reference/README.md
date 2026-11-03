# pricing

Small pricing library for the web shop: turns an order into a quote (subtotal, discount, tax, total) and renders
a plain-text receipt.

## Discounts

The discount rate for a customer is decided in one place, `DiscountPolicy.rateFor`:

| Customer                      | Rate |
|-------------------------------|------|
| Employee                      | 20%  |
| Student                       | 10%  |
| Loyalty points >= 2000        | 15%  |
| Loyalty points >= 500         | 5%   |
| Everyone else                 | 0%   |

Students who are also loyalty members do not get both: the larger of the two rates applies.

All money is `BigDecimal` with two decimals, rounded half up (see `Money`).

## Running the tests

The project has no build tool. Put the JUnit 5 console launcher at `lib/junit-platform-console-standalone.jar`,
then run

    java tools/RunTests.java

It compiles everything under `src/` into `build/` and runs every test.
