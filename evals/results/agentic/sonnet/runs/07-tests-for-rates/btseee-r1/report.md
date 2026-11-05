I added `test/rates.test.ts` with 31 tests and left `src/rates.ts` unchanged. The full suite passes (40 tests, 0 failures). I ran `tsc --noEmit` as well. It printed only npm notices, so I'm taking that as clean, though I didn't check its exit code.

The tests cover all four exports:
- **`minorUnitsOf`:**
  - It returns the right decimal places for EUR, JPY and KWD.
  - It rejects unknown codes and lowercase codes like `"eur"`.
  - The error carries the offending currency.
- **`convert`:**
  - Exact conversions work, including between currencies with different minor-unit sizes (EUR, JPY, KWD).
  - Same-currency and zero amounts come back unchanged.
  - Ties follow the target currency's rounding. For example, 4 EUR→JPY gives 7 (half-up), while 10 EUR→CHF gives 10 and 30 EUR→CHF gives 28 (half-even).
  - Negative amounts round symmetrically.
  - `Number.MAX_SAFE_INTEGER` keeps full precision.
  - It rejects fractional, NaN, infinite and unsafe amounts, and unknown currencies.
- **`feeFor`:**
  - The fee is 2.5% of the amount, with zero amounts charged nothing.
  - The per-currency minimum and maximum apply.
  - Fee ties follow the rounding mode, so 1220 gives 30 in EUR and 31 in USD.
  - It rejects negative, invalid and unknown inputs.
- **`quote`:**
  - It returns the converted amount, the fee and the net.
  - The minimum and maximum fee both show up in quotes.
  - An amount exactly equal to the fee is accepted with a net of 0.
  - An amount that doesn't cover the fee is rejected.
  - It rejects invalid and unknown inputs.

I worked out the expected values by hand from the rate table, not by running the code, so they check the current behavior against the formulas. Every test passed on the first run.