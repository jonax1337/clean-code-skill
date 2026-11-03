I added `test/rates.test.ts` with 31 tests for `src/rates.ts`, and `src/rates.ts` itself is untouched. `npm test` passes 39 of 39, which is the 31 new tests plus the 8 that were already there. `npm run typecheck` printed no errors. I haven't committed anything.

The suite covers all four exports (`minorUnitsOf`, `convert`, `feeFor`, `quote`):
- **`convert`:**
  - Conversion across 0-, 2- and 3-decimal currencies.
  - Same-currency and zero amounts.
  - Rounding ties for each currency's mode. Half-even and half-up are told apart with values where they differ, such as 10 and 30 EUR cents into CHF, and 15 EUR cents into USD.
  - Negative ties rounding the same way as positive ones.
  - The largest safe integer converted without losing precision.
- **`feeFor`:**
  - The 2.5% fee.
  - The minimum and maximum fee for EUR, JPY and KWD, including the exact amounts where the fee switches between the minimum, the percentage and the cap.
  - A rounding tie on the fee that comes out differently for EUR and USD.
  - Zero amounts.
- **`quote`:** converted amount, fee and net together, an amount that exactly covers the fee (accepted), and one cent less (rejected).
- **Errors:** negative, fractional, `NaN`, infinite and unsafe amounts raise `InvalidAmountError`. Unknown or lowercase currency codes raise `UnknownCurrencyError`.

Two of my first expected values were wrong because of my own arithmetic. I corrected the tests by recalculating by hand, not by copying what the code returned. The code was right both times.

One behavior to keep in mind while you change the module: `quote` on a negative amount fails inside `feeFor` with a "no fee on a negative amount" message. That's now pinned by a test, so changing it will show up as a failure.