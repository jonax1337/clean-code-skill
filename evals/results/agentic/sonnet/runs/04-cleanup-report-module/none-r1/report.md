I've rewritten `src/report.js`, and its output is unchanged. I haven't committed it.

To check that, I ran the original and the new version side by side on 20,000 random inputs. The inputs covered all regions, an unknown region, `units` of 0 or below, month filters, long product names, bulk and large orders, and negative amounts. I also compared `formatMoney` directly. There were no differences, and the 5 existing tests pass.

**What changed**
- **One loop instead of three:** the DE, FR and UK blocks were near-copies written three different ways. Now one loop reads a small `REGIONS` table (title and tax rate) and uses one row-building path.
- **Shared helpers:** `grossAmount`, `truncate`, `groupThousands` and `validateOptions` replace the repeated code. The magic numbers (`0.95`, `100`, `10000`, column widths) are named constants.
- **Dead code removed:**
  - the `format === 'legacy'` branch, which could never run because any non-`text` format throws first
  - the commented-out void and quarter filters
- **Kept as before:** the column layout, the section order, the error messages, and the header comment and US-region TODO.

**One quirk I kept on purpose.** When a row's amount is negative (a negative `unitPrice` or a discount over 100%), the old code printed odd signs:
- UK printed `£-2,914,061.95`.
- DE and UK counted the `-` as a digit when grouping, so a short value came out as `-.123 €`.

I didn't fix this because the finance import reads this output and might depend on it. The quirk now sits in one function, `formatRowMoney`, with a comment. If negative amounts are real in your data, it's worth asking finance whether to correct it. That would be a deliberate change to the output, separate from this cleanup.

The existing tests only cover DE and the empty case. I didn't add tests, but the comparison script is in `/tmp/cmp/fuzz.mjs` if you want to turn it into a permanent test.