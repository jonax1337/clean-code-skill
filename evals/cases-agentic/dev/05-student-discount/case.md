# Student discount next to the loyalty discount (Java)

Tests adding a small business rule to an existing pricing library: a 10% student discount that must not be combined with the loyalty discount (a student who also has loyalty points gets whichever rate is larger, never both). The rate selection lives in one method, `DiscountPolicy.rateFor`, and two entry points (`PriceCalculator.quote` and `discountedUnitPrice`) plus the receipt depend on it. The traps are over-engineering a single rule (strategy interface, factory or registry, new layers), special-casing students in the calculator so the catalog price or the quote drifts, stacking or mis-ordering the two rates, leaving the codebase's single `BigDecimal` / half-up rounding convention (double, another `RoundingMode`), and editing or loosening existing tests instead of adding new ones.

## Prompt

We want to give students 10% off. Can you add a `STUDENT` customer type for that? A student can also be a loyalty member, but the two discounts shouldn't be combined, so they just get whichever one is bigger.
