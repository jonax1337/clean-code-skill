I rewrote `src/report.js`, and its output is unchanged. Before and after, a 200,000-case randomized comparison showed 0 differences. The 5 existing tests pass, and the sample finance export is identical.

The comparison covered all three regions plus an unknown one, negative and zero values, discounts, the bulk threshold, the large-order marker, long product names, and the month and format options.

**What changed**
- The three copy-pasted region blocks are now one `appendSection`, driven by a small `REGIONS` table (code, title, VAT rate).
- Pricing is one `grossAmount` function. Small helpers cover rounding, name truncation, and building a row.
- Magic numbers (100 units, 0.95, 10000, column widths) are named constants.
- I removed dead code:
  - the `legacy` format branch, which could never run because any format other than `text` throws earlier;
  - the commented-out void filter and quarter filter.
- `formatMoney` is now simpler but behaves the same. `digest.js` and `export.js` still import it as before.

**Odd behavior I kept on purpose.** For negative amounts, the row lines and the subtotals format the minus sign differently. For example, a UK credit row prints `£-20.00`, while the subtotal prints `-£20.00`. A DE row of `-123` prints `-.123,00`. You said the output must stay exactly the same, so I kept this as `rowGroupers` and documented it in a comment. It looks like a bug, but only finance can say whether their import depends on it.

**Open points**
- The tests only cover German sales, so the French and UK sections are protected only by my comparison against the old file. That script is in a temp folder outside the repo (`cc-agentic-8h1zk70h/baseline`). If you want it kept, I can turn it into proper regression tests.
- `src/report.js` has no `.clean/` context in this repo, so I worked from the code and its neighbors. I didn't commit anything.