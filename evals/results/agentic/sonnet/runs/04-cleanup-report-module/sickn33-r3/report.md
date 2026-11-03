I've cleaned up `src/report.js`. It produces the same output as before, and I haven't committed anything.

To check that, I kept a copy of the original and ran both versions on 20,000 random inputs. The inputs covered all regions, refunds, month filters, bad options, long product names and large amounts. The two versions gave identical output on every one. The existing tests pass, plus one new test.

**What changed**
- The Germany, France and UK blocks were three near-identical copies. They're now one section builder driven by a small `REGIONS` table (code, title, tax rate).
- `buildReport` now reads as a short top-down summary. Each step has its own small function with a name: `validateOptions`, `selectAndSortSales`, `buildRegionSection`, `grossAmount`, `formatSaleLine`.
- The magic numbers are named constants, and the one-letter variables are gone.
- I removed dead code: the `legacy` format branch could never run, because the format check throws before reaching it. I also removed the commented-out `void` filter and `quarter` code. Git history still has them.
- `formatMoney`'s signature and output are unchanged, so `digest.js` is unaffected. The file's header comment and the US-region TODO are kept.

**A bug I kept on purpose.** For negative amounts (refunds), the old Germany and UK sale lines put the minus sign inside the digit grouping. For example, they print `-.995,97 €` and `£-,230,770.34`, where the subtotal lines print `-995,97 €`. Fixing that would change what the finance import receives. I kept the old output, isolated it in `formatLineMoney` with a comment, and added a test that pins it. If the import doesn't depend on it, fixing it is a one-line change, but please decide that with finance.

The only inputs that could behave differently are an `Infinity` unit price combined with a zero discount, which can't come from JSON.