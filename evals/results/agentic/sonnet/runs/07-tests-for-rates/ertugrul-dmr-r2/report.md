I added `test/rates.test.ts` with 33 tests for `src/rates.ts`, and I didn't touch `src/rates.ts`. The full suite passes (41 tests, 0 failures), each test runs in well under 100ms, and `tsc --noEmit` is clean.

The tests cover all four exports:
- **`minorUnitsOf`**: every supported currency, unknown and empty codes, and lowercase codes (which are rejected today).
- **`convert`**:
  - Same-currency and zero amounts, and conversions between currencies with different minor units (EUR, JPY, KWD).
  - Exact ties for half-up and half-even targets, such as 4 EUR cents → 7 JPY and 30 EUR cents → 28 CHF.
  - Negative amounts, which round symmetrically to positive ones.
  - Amounts up to `MAX_SAFE_INTEGER`.
  - Rejection of non-integer, NaN, infinite and unsafe amounts.
  - Unknown source and target currencies.
- **`feeFor`**: the 2.5% fee, a zero amount, and the minimum and maximum fee at and around their boundaries. Also tie rounding by currency, negative amounts, and invalid amounts and currencies.
- **`quote`**: the converted/fee/net result, the fee charged in the target currency, an amount that exactly covers the fee, an amount that doesn't, and a zero amount. Also negative amounts and invalid input.

The tests pin down the code's current behavior, so some results may look odd:
- Currency codes are case-sensitive.
- `quote` of 0 returns all zeros rather than throwing.
- A negative `quote` throws only because `feeFor` rejects negatives.

If you plan to change any of those, expect the matching tests to fail on purpose.