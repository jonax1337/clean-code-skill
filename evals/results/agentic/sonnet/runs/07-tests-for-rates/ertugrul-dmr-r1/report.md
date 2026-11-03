I added `test/rates.test.ts` with 29 tests for `src/rates.ts`. The full suite of 45 tests passes, `tsc --noEmit` is clean, and `src/rates.ts` is untouched. The new file isn't committed.

One test failed on the first run because of my own arithmetic: 1000 JPY is 615 EUR cents, not 1. I fixed the expectation, not the code.

What the tests cover:
- **`minorUnitsOf`:**
  - All five currencies.
  - Unknown codes, including lowercase `eur` and the empty string.
  - The `currency` field and message on `UnknownCurrencyError`.
- **`convert`:**
  - Each currency's rate, including conversions between currencies with different minor units (JPY, KWD) and cross rates through the euro.
  - Identity conversions, zero and negative amounts.
  - Ties: half-up rounds away from zero and half-even rounds to the even neighbour, each checked for positive and negative amounts. The values are chosen so the two modes give different results.
  - Exact results at `MAX_SAFE_INTEGER`.
  - Rejection of fractional, `NaN`, `Infinity` and unsafe amounts, and of unknown source or target currencies.
- **`feeFor`:**
  - The 2.5% fee, zero amounts, the minimum fee, and the exact point where the percentage takes over from the minimum.
  - The maximum fee, including at `MAX_SAFE_INTEGER`.
  - Tie rules per currency (USD, EUR, JPY, KWD).
  - Rejection of negative, invalid and unknown-currency input.
- **`quote`:**
  - The normal path and the target currency's minimum and maximum fee.
  - Zero amounts, and an amount that exactly covers the fee (net 0) versus one unit short (throws).
  - The error message, and rejection of negative, invalid and unknown-currency input.

I wrote the expected values by hand from the rate table and rounding rules, then ran them against the current code. Where the tests pass, they describe what `rates.ts` does today, so they will catch behavior changes when you edit it.