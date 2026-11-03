`mergeContacts` is now fast: on a 50k existing / 30k incoming dataset it takes about 30 ms, down from about 110 seconds.

**Cause:** for every incoming contact, `findIndex` scanned the whole result array and re-normalized each entry's email, so the cost grew with the product of the two list sizes.

**Fix** (in `src/import.ts`, the only file changed): I build a `Map` from normalized email to position once, then each incoming contact is an O(1) lookup. Behavior is unchanged: when the existing list already has duplicate emails, the first one still wins, and new contacts are still appended in arrival order.

**Verification:**
- `npm test`: 8/8 pass, same as before.
- `npm run typecheck`: exits 0.
- Equivalence: I compared the old and new functions on 200 random inputs with duplicates on both sides and mixed casing/whitespace. The outputs were identical.
- Timing: the benchmark ran in a scratch directory, which I've since deleted. It used synthetic data, so real CSVs may differ a little, but the complexity change is what matters here.

I didn't commit anything. I didn't look at `csv.ts` or `pipeline.ts`; you said the time goes into `mergeContacts`, and the benchmark only covered that function, so if the full upload still feels slow, parsing or serialization would be the next place to check.