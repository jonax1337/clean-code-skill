I added `test/rates.test.ts` with 31 tests covering `minorUnitsOf`, `convert`, `feeFor` and `quote`. `src/rates.ts` is untouched. The full suite passes (38 tests, 0 failures) and `tsc --noEmit` reports no errors. I haven't committed anything.

- **`convert`**:
  - Same-currency and cross-currency rates, and rescaling between 0, 2 and 3 decimal places.
  - Non-tie rounding.
  - Ties: half-up goes away from zero (USD, JPY), half-even goes to the even neighbor (CHF, KWD).
  - Negative amounts mirror positive ones, and zero stays zero.
  - Exact results at `MAX_SAFE_INTEGER`.
  - Rejection of fractional, `NaN`, infinite and unsafe amounts, and of unknown currencies on either side.
- **`feeFor`**:
  - The 2.5% fee, plus the minimum and maximum, including amounts landing exactly on each.
  - Zero is free.
  - Percentage ties follow the currency's rounding mode.
  - Negative amounts, fractional amounts and unknown currencies are rejected.
- **`quote`**:
  - Converted, fee and net values.
  - An amount that exactly covers the fee gives net 0.
  - An amount that falls short throws.
  - Zero, negative amounts and unknown currencies.
- **`minorUnitsOf`**: known currencies, plus rejection of unknown and lowercase codes.

My first run had two failures, both from my own arithmetic: 100.00 EUR is 16,250 JPY, not 162,500. I fixed the expected values in the tests, not the code.

There's no dedicated `quote` test where the fee hits the maximum.

I couldn't run the mutator, crapper or dryer tools from the skill, because I didn't find them in this environment.