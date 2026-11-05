I added `test/rates.test.ts`, and `src/rates.ts` is unchanged. `npm test` passes (38 tests across the whole suite) and `npm run typecheck` is clean. I haven't committed anything.

The tests cover all four exports: `minorUnitsOf`, `convert`, `feeFor` and `quote`.

- **Rate conversion:** conversions between currencies with 0, 2 and 3 decimal places, identity conversion, zero, and exactness on very large amounts.
- **Rounding:** ties round away from zero for half-up currencies and to the even neighbour for half-even ones, in both `convert` and `feeFor`. Negative amounts round symmetrically.
- **Fees:** the 2.5% rate, the per-currency minimum and maximum, the exact point where the minimum stops applying, and zero amounts.
- **`quote`:** the converted/fee/net result, an amount that exactly covers the fee, and an amount that is too small for it.
- **Errors:** unknown or wrongly cased currencies (including the `currency` field on the error), fractional, NaN, infinite and unsafe integers, and negative amounts in `feeFor` and `quote`.

On the first run, two of my own expected values were wrong. I had made arithmetic slips in the JPY quote and the KWD fee cap, not found bugs in the code. I corrected the expectations, and every expected value is now worked out by hand from the rate table.