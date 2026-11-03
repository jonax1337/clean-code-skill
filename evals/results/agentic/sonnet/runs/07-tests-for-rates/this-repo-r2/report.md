I added `test/rates.test.ts` and left `src/rates.ts` untouched. `npm test` passes all 43 tests, which includes the existing suites. `npm run typecheck` ran with no errors.

The suite covers `minorUnitsOf`, `convert`, `feeFor` and `quote`:
- **Rounding:** exact ties under both modes, and negative ties rounding the same as positive ones. Half-up and half-even give different results on these cases, so the tests tell the modes apart.
- **Fee limits:** the 2.5% fee, zero amount, the minimum and maximum fee in each currency, and amounts exactly at each limit.
- **`quote`:** conversion plus fee, an amount that exactly covers the fee (net 0), and an amount that falls short and throws.
- **Errors:** unknown currencies, lowercase codes, negative amounts for fees, and non-integer, NaN, infinite or unsafe amounts.
- **Precision:** the largest safe integer converts exactly.

One test failed on the first run. The cause was my own arithmetic in the expected value, and the code was fine: 1 KWD is 308 EUR cents, and I had written 3077. I fixed the test.

I checked every expected value by hand from the rate table and did not copy it from the code's output. A few of them pin current behavior that you may want to look at before you change the module:
- `quote` on a negative amount throws "No fee can be charged", not a conversion error.
- `convert` accepts negative amounts, while `feeFor` rejects them.
- The fee is rounded with the target currency's mode.