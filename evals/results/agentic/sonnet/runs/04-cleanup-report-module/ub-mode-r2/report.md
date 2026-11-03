I cleaned up `src/report.js`, and the finance output is unchanged for every valid input I tested. It differs in two edge cases (below). The 8 tests pass. I committed locally but haven't pushed.

## What changed
- **One region table.** The three copy-pasted blocks (DE, FR, UK) are now one loop over a `REGIONS` table. Adding the US means adding one entry, plus its formatting rule in `formatMoney`.
- **Shared helpers.** The price calculation, product-name truncation and row layout are now `grossAmount`, `truncate` and `saleLine`. Rows use `formatMoney` instead of three separate thousand-separator implementations.
- **Named constants.** The magic numbers (20, 5, 14, 100, 0.95, 10000) now have names.
- **Dead code removed.** I deleted the `legacy` format branch, which could never run because any format other than `text` throws earlier. I also deleted the commented-out void filter and quarter filter.
- `formatMoney` and `buildReport` keep the same signatures, so `export.js` and `digest.js` are untouched.

## How I checked it
- Before touching the code, I added tests that pin the current output exactly. They cover the sample data with all three regions, a large-order `*`, a truncated name, the month filter, the error messages, and `formatMoney` per region. These passed against the old code and still pass.
- I ran about 100,000 random cases through both the old and new code and compared the output. The cases varied region, units (including the 100-unit rebate), discounts, month filters, formats, long names and amounts of £10,000 and over. The output was identical for valid data.

## Where the output differs
Both cases need bad data, so I didn't carry the old behaviour over:
1. **Negative `unitPrice` or a discount over 100%.** The old code printed malformed amounts for UK and DE, such as `£-57,000.00` or `£-,280.14`. The new code prints `-£57,000.00`. French amounts were already correct.
2. **A `discountPct` that isn't a number in FR.** The old code printed `NaN` for that row, and the other regions ignored the bad discount. The new code ignores it in all three.

If finance's import might depend on either behaviour, I can restore the old output exactly, but that means keeping the old per-region formatting quirks. I'd rather you decide.

## Not done
I didn't run the crapper, dryer or mutator checks from the skill, because I don't have those tools here. The duplication is gone and the largest function is now small, but I didn't measure it.

## Log
1. Read `report.js`, its callers and its tests.
2. Saved the old file outside the repo and wrote a script to compare old and new output.
3. Committed the pinning tests (`40b4449`).
4. Rewrote `report.js` and committed it (`67008e3`).