`mergeContacts` now runs in about 35 ms on your scale instead of roughly 87 seconds. The change is in `src/import.ts`, and I haven't committed it.

**The cause:** for every incoming contact, the code called `findIndex` over the whole result list and re-normalized each existing email on every comparison. With 50k existing and 30k incoming, that is on the order of 1.5 billion normalizations.

**The fix:** I build a `Map` from normalized email to position in the result once, up front. Each incoming contact is then a single lookup. Two details keep the behavior the same:
- If `existing` already has duplicate emails, the first one wins, as `findIndex` did.
- New contacts are added to the map as they are appended, so duplicates within the incoming list still merge with each other.

**Verification:**
- `npm test`: all 8 tests pass.
- `npm run typecheck`: clean.
- Benchmark with identical inputs (50k existing, 30k incoming, 55k output): the original took 87,308 ms and the new version 35 ms. The output was byte-for-byte identical (`JSON.stringify` comparison).

The benchmark scripts were in a scratch folder outside the repo. Another part of the stack may still be slow for large uploads, since `importCsv` also parses both CSVs and serializes the result. I didn't profile those.