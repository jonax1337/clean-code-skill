I've refactored `src/report.js`, and the report output is unchanged. I ran 20,000 random sales sets through the old and new `buildReport` and found no differences. The 5 existing tests pass. I also compared `formatMoney` on its own across all regions and several values, including negatives, and it matched too.

The file is about 125 lines, down from about 190. The three nearly identical sections (Germany, France, UK) were copy-pasted with small variations. They're now one loop over a small table of region, title and tax rate. The money formatting, the amount calculation and the row layout are each a separate function with a name, and the magic numbers are named constants.

`formatMoney`'s exports and behavior are the same, so `digest.js` and `export.js` need no changes.

- **Dead code removed:** I deleted the commented-out `void` and `quarter` filters. I also deleted the `legacy` format branch, which couldn't be reached because any format other than `text` throws earlier.
- **Negative amounts:** In the old code, a negative row amount (negative unit price, or a discount over 100%) was formatted oddly. For example, UK gave `£-7,110.74` and DE could give `-.123,00 €`. Subtotals formatted the same amount correctly. I kept the odd row output so the finance import sees identical text, and isolated it in `formatRowMoney` with a comment. If negative rows never occur in real data, you can delete that function and the output will then be cleaner and consistent.
- **Not committed:** The changes are in the working tree only.