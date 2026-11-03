`mergeContacts` is now linear instead of quadratic. A 50k-existing / 30k-incoming merge takes about 43 ms in my benchmark.

**The cause:** for each incoming contact, `findIndex` scanned the whole result array and re-normalized every email on each comparison. That is roughly 1.5 billion normalizations at your scale.

**The fix** (in `src/import.ts`): I build a `Map` from normalized email to index once, then each incoming contact is a single lookup. Behavior is unchanged:
- When existing data has duplicate emails, the first entry still wins, as with `findIndex`.
- New contacts are appended in arrival order, and duplicates within the incoming list still merge with each other.
- Merges still replace the entry at its existing index, so the map stays valid.

**Verification:**
- All 8 tests pass (`node --test test/`).
- `tsc --noEmit` passes.
- The benchmark was a one-off script with synthetic data, which I deleted afterward. I didn't time an actual CSV upload end to end. Parsing (`parseContactsCsv`) and serialization (`toContactsCsv`) are outside this change, so if the upload is still slow after this, look there next. I didn't read `csv.ts`, so I can't say whether it has similar problems.

I didn't commit anything.