I rewrote `src/report.js`, and the output is unchanged. I checked this by running the original and the new version on 5,000 random inputs and comparing the results byte for byte. There were no differences. The inputs covered DE, FR, UK, an unknown region, negative prices, huge amounts, long product names, month filters and the error cases. `formatMoney` also matched, and the 5 existing tests pass.

**What changed**
- The Germany, France and UK blocks were three copies of the same logic written three different ways. They are now one pipeline driven by a `REGIONS` table (code, title, tax rate, line-amount format).
- `buildReport` now reads as a short outline: validate options, select rows, build one section per region, then add the totals.
- The helpers are `validateOptions`, `selectRows`, `buildRegionSection`, `grossAmount`, `formatSaleLine` and `truncateProduct`. Single-letter names are gone, and the magic numbers are now named constants.
- I removed code that never ran: the `format === 'legacy'` branch (a legacy format already throws "unsupported format" at the top of the function) and the commented-out `void` and `quarter` filters.
- The header comment and the US TODO are still there.

**What I left alone on purpose**
- The three regions format negative line amounts differently. For example, in Germany an amount of -123 renders as `-.123,00 €`, which looks like a bug. I kept each region's own grouping function so the finance import gets exactly what it gets today. If you want it fixed, that's a separate change, and the finance team should hear about it first.
- `formatMoney` is unchanged apart from variable names, because `digest.js` uses it.

The existing tests only cover Germany. The reference copy and comparison script are in `..\ref` (outside the repo) if you want to rerun them. I haven't committed anything. I can turn the FR, UK, negative-amount and large-order cases into real tests in `test/report.test.js` if you want.