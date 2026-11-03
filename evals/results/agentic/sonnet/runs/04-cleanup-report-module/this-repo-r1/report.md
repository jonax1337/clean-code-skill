I rewrote `src/report.js` and its output is unchanged. The other tests pass, and I added five new tests to `test/report.test.js`. I haven't committed anything.

## What changed
The three near-identical region blocks (DE, FR, UK) are now one loop over a `REGIONS` table (code, title, VAT rate). The shared pieces each got a name:
- `grossAmount`
- `formatRow`
- `truncate`
- `buildRegionSection`
- `groupThousands`, which replaces three different ways of adding thousands separators

Magic numbers are now constants, and I removed the dead and commented-out code. The file went from 188 to about 150 lines. Adding the US region is now one table entry plus a case in the two money formatters. The public API is the same: `buildReport` and `formatMoney` have the same signatures.

## How I checked the output is the same
- **Tests:** `node --test` gives 10 passed, 0 failed. The 5 new tests (France, UK, month filter, errors, negative amounts) also pass against the original code, so they describe what it did before.
- **Comparison with the original:** I ran the old and new `buildReport` side by side on 200,000 random inputs, twice. The second run included refunds. Every output was identical, including error messages. The inputs covered:
  - unknown regions
  - zero and fractional units
  - missing prices (NaN)
  - month filters
  - every `format` value
- I did not run `cli.js`, `export.js` or `digest.js` myself. Only their tests ran, and `digest.js` uses `formatMoney`, which I kept identical.

## Things you should know
- **Removed dead code:** `format: 'legacy'` could never run, because the check at the top throws for any format other than `'text'`. The error behaviour is the same.
- **Likely bugs I left in place:** you asked for identical output, so I kept these and pinned them with a test.
  - Negative row amounts print oddly in DE and UK, for example `-.119,00 €` and `£-,120,000.00`. The subtotal for the same rows prints correctly.
  - A sale with a missing price gives a subtotal like `,aN €`.
  - Sales from regions other than DE, FR and UK are silently left out of the report.
  - The negative-amount quirk has a comment in the code. If finance's import doesn't need it, fixing it is a small change, but ask them first.