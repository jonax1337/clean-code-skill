I added `test/rates.test.ts` and left `src/rates.ts` untouched. The full suite passes (45 tests, 0 failures) and `tsc --noEmit` is clean. I didn't commit anything.

The tests cover all four exports: `minorUnitsOf`, `convert`, `feeFor` and `quote`.

- **`minorUnitsOf`:** Checks each currency's minor units. It also checks that unknown or wrong-case codes throw `UnknownCurrencyError`, and that the error carries the offending code.
- **`convert`:**
  - It checks exact conversions across currencies with different minor units (EUR/JPY/KWD), same-currency identity, zero, and `MAX_SAFE_INTEGER`.
  - Tie-rounding cases are hand-computed: half-up for USD and JPY, half-even for EUR, CHF and KWD, including negative amounts.
  - It also checks that non-integer, NaN, infinite and unsafe amounts throw.
- **`feeFor`:** Checks the 2.5% fee, zero amount, minimum and maximum clamping with the exact boundaries, rounding mode on the percentage, and errors for negative or invalid amounts and unknown currencies.
- **`quote`:** Checks a full quote, the min and max fees, `net + fee = converted`, and zero. It also checks that an amount exactly covering the fee gives net 0, and that an amount below the fee throws.

I took the expected values from the code's current behavior, which I read as intended. One case to check when you change the module: a negative amount in `quote` throws from `feeFor`, not from `convert`.