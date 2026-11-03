I rewrote `src/report.js`. Its output is unchanged, and I'm leaving the commit to you.

**How I checked it:** I kept a copy of the original and ran it against the new version on 40,000 random cases. These covered all three regions, other regions, zero and negative units and prices, discounts, the 100-unit bulk threshold, month filters, bad options, and `formatMoney` with unknown regions. There were 0 mismatches. `npm test` passes: 13 tests, 0 failures. The 8 new tests also pass against the original file, so they describe what it did before my change.

**What changed:**
- The three copy-pasted sections (Germany, France, UK) are now one loop over a small `REGIONS` table. It holds each region's title, tax rate, separator and number format. Adding the US later means adding one entry.
- The price and tax calculation is one function, `grossAmount`. The product-name truncation and row layout are one function, `formatRow`. Option checks and month filtering are separate small functions.
- The magic numbers (100 units, 0.95, 10000, column widths) are named constants.
- I removed the unreachable `legacy` branch and the commented-out code. `format: 'legacy'` already threw "unsupported format" before reaching that branch, and it still does.
- I kept the header comment about the finance import and the US TODO.
- The exports `formatMoney` and `buildReport` have the same signatures.

**A bug I kept on purpose:** for negative sales (a negative unit price), the DE and UK row amounts print wrongly. For example, a -123.45 DE sale prints `-.146,91 €`, and a UK one prints `£-,148.14`. The minus sign gets counted as a digit when the thousands separators are placed. France and the subtotal lines are fine. Since finance parses this output, I kept the behavior, isolated it in `formatRowMoney`, and pinned it with a test whose comment calls it a known quirk. I don't know whether negative sales actually occur. If they do, it's worth raising with finance. Fixing it later is a one-function change.

My comparison script is in the `scratch` folder next to the repo, outside git. The existing `export.js` and `digest.js` tests still pass.