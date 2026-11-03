I added `test/rates.test.ts` with 31 tests for `src/rates.ts`, and I didn't change `src/rates.ts` or any other existing file. `npm test` shows 40 passed and 0 failed across the whole repo, and `npm run typecheck` printed no errors.

The tests cover:
- **`minorUnitsOf`:** all five currencies, plus unknown and lowercase codes.
- **`convert`:**
  - Conversions between currencies with different minor units, and through the euro (USD to CHF).
  - Rounding of ties, positive and negative: half-up targets (USD, JPY) round away from zero, and half-even targets (KWD) round to the even neighbor.
  - Non-tie rounding, zero, same-currency conversion, and the largest safe integer, where the result is exact.
  - Rejection of fractional, NaN, infinite and unsafe amounts, and of unknown currencies.
- **`feeFor`:**
  - The 2.5% rate and the zero amount.
  - The minimum and maximum fee in each currency, at their exact boundaries.
  - The same tie amounts giving different fees for EUR (half-even) and USD (half-up).
  - Rejection of negative amounts.
- **`quote`:** the full result, an amount that exactly covers the fee (net 0), one that doesn't cover it, zero, and negative or invalid input.

One of my own expected values was wrong at first (a JPY quote). The code was right, and I corrected the test.

The tests record what the code does today, including a few choices you may want to look at before changing it:
- `quote` rejects negative amounts only because `feeFor` does.
- Half-even and half-up rounding are set per target currency, so the same amount can give different fees in EUR and USD.
- I didn't add tests for the CHF and KWD rates beyond the fee limits and a few conversions.

I haven't committed anything.