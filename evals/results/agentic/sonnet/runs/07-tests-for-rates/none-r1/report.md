I added `test/rates.test.ts` with 29 tests for `src/rates.ts`. The full suite passes (40 tests) and the typecheck is clean. Only the new test file was added, and I didn't touch `rates.ts`. I haven't committed anything.

The tests cover all four exported functions:
- **`minorUnitsOf`:** it returns the right decimal places for every currency. Unknown or wrongly cased codes throw `UnknownCurrencyError`, and the error carries the offending code.
- **`convert`:**
  - Same-currency conversion returns the amount unchanged, and the euro rate is applied correctly.
  - Currencies with different minor units work: EUR→KWD (3 decimals) and EUR→JPY (0 decimals).
  - Ties round as the target currency specifies (half-up for USD and JPY, half-even for CHF and KWD).
  - Negative ties round by magnitude, so −5 EUR cents to USD gives −6.
  - Amounts up to `MAX_SAFE_INTEGER` stay exact.
  - Non-integers, `NaN`, `Infinity` and unsafe integers throw `InvalidAmountError`.
- **`feeFor`:** 2.5% with the minimum and maximum applied per currency, including amounts that land exactly on a limit. Zero amounts cost nothing, percentage ties follow each currency's rounding mode, and negative or invalid amounts throw.
- **`quote`:** the fee is charged in the target currency. An amount exactly equal to the fee gives a net of 0, and an amount below the fee throws. Zero, negative, invalid and unknown-currency inputs are covered too.

I worked out the expected values by hand from the rate table rather than copying them from the function's output. That way the tests describe the intended behavior, which matters since you're about to change the code.