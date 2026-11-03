I added `test/rates.test.ts` with 31 tests for `src/rates.ts`. The full suite passes (39 tests) and the typecheck is clean. I didn't touch `src/rates.ts`, and I haven't committed anything.

The tests cover:
- **`minorUnitsOf`:** the minor-unit counts for the supported currencies, unknown or wrongly cased codes, and the currency carried on the error.
- **`convert`:**
  - Same-currency conversion, euro-rate conversion, and currencies with different minor units (JPY with 0 decimals, KWD with 3).
  - Rounding ties: half-up for JPY, half-even for CHF, including negative amounts. For example, 100 EUR cents to JPY gives 163 (162.5 rounds up), and 30 EUR cents to CHF gives 28 (28.5 goes to the even neighbor).
  - Zero amounts, the largest safe integer, unknown currencies, and invalid amounts (fractions, NaN, Infinity, unsafe integers).
- **`feeFor`:**
  - The 2.5% fee, a zero fee for zero amounts, and the per-currency minimum and maximum, including exactly at each limit.
  - Fee ties that round differently under half-even (EUR) and half-up (USD).
  - Negative, non-integer and unknown-currency errors.
- **`quote`:** the full `{converted, fee, net}` result, zero amounts, an amount that exactly covers the fee (net 0), amounts that don't cover it, and error propagation.

I worked out the expected values by hand from the rate table, not by copying the code's output. The rate table, fee limits and rounding modes are therefore pinned by these tests, so a change to any of them will fail a test and you'll need to update the expected values. I didn't run any mutation checks to confirm the tests catch bugs.