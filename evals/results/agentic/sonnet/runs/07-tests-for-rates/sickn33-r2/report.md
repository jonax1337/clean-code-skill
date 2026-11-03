I added `test/rates.test.ts` with 33 tests for `src/rates.ts` and didn't touch the code itself. The full suite passes (41 tests) and `tsc --noEmit` is clean. I haven't committed anything.

The tests cover all four exports (`minorUnitsOf`, `convert`, `feeFor`, `quote`):

- **`minorUnitsOf`:** it returns the right decimals for each currency and rejects unknown or lower-case codes. The error carries the bad currency.
- **`convert`:**
  - Conversions go via the euro, including between two non-euro currencies and currencies with different minor-unit sizes.
  - Converting a currency to itself, zero, negative amounts and very large amounts all come out exact.
  - Half-up currencies (USD, JPY) round ties away from zero, including negative amounts. Half-even currencies (CHF, KWD) round ties to the even neighbour.
  - Fractional, `NaN`, infinite and unsafe-integer amounts are rejected, and so are unknown currencies on either side.
- **`feeFor`:**
  - The fee is 2.5%, with zero giving zero.
  - The minimum and maximum fees apply, and the tests check the exact boundaries where the fee switches between them and the percentage.
  - Tie rounding differs by currency: EUR is half-even and USD is half-up.
  - Negative, fractional and unknown-currency inputs are rejected.
- **`quote`:** it returns converted, fee and net. An amount that exactly covers the fee gives a net of 0, and one that falls short is rejected. Zero quotes as all zeros, and bad amounts or currencies are rejected.

I worked out the expected values by hand from the rate table rather than copying the code's output. That way, the tests describe what the module should do rather than just mirroring what it does now.