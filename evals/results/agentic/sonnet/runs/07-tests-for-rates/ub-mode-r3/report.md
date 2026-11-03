I've added `test/rates.test.ts` with 29 tests for `convert`, `feeFor`, `quote` and `minorUnitsOf`. The full suite passes (40 tests) and `npm run typecheck` is clean. I left `src/rates.ts` alone.

I committed the file locally but did not push. I also didn't run the crapper, dryer or mutator tools from the skill, so there's no complexity or mutation-coverage check on `rates.ts` yet.

Expected values come from working through the rates by hand, and they passed on the first run. So the tests describe what the code does today, which is what you want before changing it.

They cover:
- **Conversion:** the euro rate, same-currency conversion, cross-currency conversion, and rescaling between minor-unit sizes (JPY has 0 decimals, KWD has 3).
- **Rounding:**
  - Exact ties for half-up and half-even targets, including negative amounts.
  - Non-tie rounding.
  - Zero.
  - An exact large amount near `MAX_SAFE_INTEGER`.
- **Fees:** the 2.5% rate, the per-currency minimum and maximum, amounts sitting exactly on those limits, tie rounding, and zero.
- **Quote:** net amount, a fee that exactly equals the converted amount (net 0), and an amount too small to cover the fee.
- **Errors:** unknown or lowercase currencies, and negative, fractional, `NaN`, infinite or unsafe amounts.

I did not try to break `rates.ts` to confirm the tests catch changes.

Say if you want me to push, or run the mutation and complexity checks first.