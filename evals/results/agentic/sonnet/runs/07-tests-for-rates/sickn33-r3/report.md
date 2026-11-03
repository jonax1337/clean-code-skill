I added `test/rates.test.ts` with 34 tests covering `convert`, `feeFor`, `quote` and `minorUnitsOf`. I didn't touch `src/rates.ts`. The full suite passes (43 tests) and the typecheck is clean.

- **`convert`:** The tests check:
  - euro rates, and conversions between currencies with 0, 2 and 3 minor units
  - the same currency on both sides, zero, and negative amounts
  - the largest safe integer
  - rounding ties: half-up goes away from zero for USD and JPY, and half-even goes to the even neighbor for EUR, CHF and KWD, with negative cases for both
  - errors: unknown currencies and non-whole or unsafe amounts
- **`feeFor`:** The tests check:
  - the 2.5% fee, a zero amount, and the minimum and maximum clamps per currency
  - the exact value where the percentage equals the minimum
  - a tie case where the rounding mode changes the fee (1300 minor units: 33 in USD, 32 in EUR)
  - errors: negative, unknown currency and non-whole amounts
- **`quote`:** The tests check:
  - the result for a normal amount, and the minimum and maximum fee
  - a zero amount, and an amount that exactly covers the fee (net 0)
  - errors: an amount that doesn't cover the fee, a negative amount, and unknown currencies

I worked out the expected values by hand from the rate table rather than copying the code's output. The one thing I didn't pin down is the rate and fee numbers themselves. If you change them, expect to update the tests that use them.