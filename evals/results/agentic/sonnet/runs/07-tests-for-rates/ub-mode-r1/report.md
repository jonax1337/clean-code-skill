I added `test/rates.test.ts` with 30 tests for `src/rates.ts`. The full suite now passes (37 tests) and the typecheck is clean. I didn't touch `src/`, and nothing is committed yet.

The tests cover:
- **`minorUnitsOf`:** the decimal places per currency, plus rejection of unknown or lowercase codes.
- **`convert`:**
  - Normal rate conversions, the same currency on both sides, and moves between currencies with different minor units (EUR, JPY, KWD).
  - Rounding: ties away from zero for half-up targets, ties to even for half-even targets, mirrored for negative amounts.
  - Edge cases: zero, `MAX_SAFE_INTEGER` staying exact, and rejection of non-integers, `NaN`, `Infinity` and unsafe integers.
  - Unknown currency on either side.
- **`feeFor`:**
  - The 2.5% fee, a zero fee for a zero amount, and the per-currency minimum and maximum.
  - The exact amounts where the minimum and maximum take over from the percentage.
  - The rounding mode applied to the percentage: 1300 cents gives 32 for EUR and 33 for USD.
  - Rejection of negative or fractional amounts and unknown currencies.
- **`quote`:**
  - The converted, fee and net breakdown, with the fee charged in the target currency.
  - Min/max fee applied to the converted amount.
  - An amount that exactly covers the fee gives net 0.
  - One that doesn't cover the fee throws.
  - Negative, fractional and unknown-currency errors.

My first run had one failing test, and the mistake was in my expected value. 1.00 EUR is exactly 162.5 JPY, a half-up tie, so the right answer is 163, not 162. The code was correct, and I fixed the test.

Two behaviours you may want to look at before you change the module:
- **Minimum fee on a tiny quote:** `quote(1, "EUR", "JPY")` throws, because the 50 JPY minimum fee exceeds the converted amount.
- **Negative quotes:** negative amounts convert fine, but `quote` rejects them because `feeFor` does.

I pinned both as they are today.

Do you want me to commit `test/rates.test.ts`?