I added `test/rates.test.ts` and left `src/rates.ts` untouched. All 46 tests in the repo pass, and `tsc --noEmit` is clean. Nothing is committed.

The suite covers all four exports:
- **`minorUnitsOf`:** every supported currency, plus unknown, lowercase and empty codes. The error's `currency` field is checked too.
- **`convert`:** euro-rate conversions, same-currency pass-through, zero, and changes in decimal places (EUR↔JPY, EUR↔KWD).
- **Rounding in `convert`:** ties under both half-up (USD, JPY) and half-even (CHF, KWD), including the even and odd neighbours. Negative amounts are checked to round symmetrically. One test confirms the target currency's rounding mode is the one applied.
- **`convert` inputs:** `Number.MAX_SAFE_INTEGER` stays exact. Non-integer, `NaN`, infinite and `2**53` amounts are rejected, as are unknown currencies on either side.
- **`feeFor`:** the 2.5% rate, zero amounts, the minimum and maximum fee per currency, and the thresholds where each applies. Also covered are half-up versus half-even rounding of the percentage (1700 gives 43 in USD and 42 in EUR), negative amounts and invalid input.
- **`quote`:** the `{ converted, fee, net }` result for EUR→USD, EUR→JPY and EUR→KWD, and that fee plus net always equals converted. It also covers an amount that exactly covers the fee (net 0), amounts below the fee, zero, and negative or invalid input.

Two of my first expected values were wrong because of my own arithmetic, and I corrected them. In both cases the code was right. If you disagree with any of these results, treat them as the current behavior being pinned, not as a spec.

A few behaviors you may want to know about before you change the module:
- A tiny non-zero amount gets the full minimum fee. `feeFor(1, "EUR")` returns 30, which is more than the amount. `quote` is what rejects that case.
- `convert` accepts negative amounts but `feeFor` rejects them, so `quote` rejects negatives as well.
- Currency codes are case-sensitive.