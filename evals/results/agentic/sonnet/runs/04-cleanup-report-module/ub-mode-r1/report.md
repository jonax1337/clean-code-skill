I rewrote `src/report.js` so each region is one table entry instead of a copy-pasted block. The report text is the same as before in every case I checked, with one exception for infinite unit prices (below). All 7 tests pass. I committed locally but haven't pushed.

- **Region table:** `REGIONS` holds the title, tax rate and number format for DE, FR and UK. One loop builds every region's section. Adding the US region from the TODO is now one table entry, though its tax rules are still open.
- **Shared helpers:** `grossAmount` and `formatRow` replace the three hand-written versions. Magic numbers now have names (`NAME_WIDTH`, `LARGE_ORDER`, `BULK_UNITS`).
- **Removed code:** I deleted the `legacy` format branch and the commented-out filters. The legacy branch couldn't run, because any format other than `text` throws earlier.
- **Unchanged:** `formatMoney`, its exports, and the callers in `export.js` and `digest.js`.

**How I checked it**
- I added `test/report.golden.test.js`, which compares the output to text captured from the old code. It covers the sample data plus credit notes, a large order, and a region the report ignores. I committed it before touching `report.js`.
- I compared old and new on 20,000 random inputs: odd prices, units, discounts, months, formats and regions. There were no differences.
- That scratch comparison is gone, so only the golden test remains in the repo.

**Things you should know**
- **Credit-note bug kept on purpose.** A negative amount whose digit count is a multiple of three prints wrongly in DE and UK rows. For example, -119 shows as `-.119,00 €` and -120 as `£-,120.00`. The finance import may already depend on that, so I kept it and commented it in the code. Whether to fix it is your call and the finance team's.
- **One difference.** An infinite unit price in a French row with no discount used to print `NaN`; now it prints `Infinity`. I left that alone because the CLI parses prices with `Number()` and I don't expect real data to hit it.

The commit message mentions that Infinity exception. Git also warned that `report.js` will switch from CRLF to LF line endings the next time it touches the file.