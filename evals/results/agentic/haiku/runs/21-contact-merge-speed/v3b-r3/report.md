`mergeContacts` in `src/import.ts` now runs in linear time. A 30k-into-50k merge takes about 33 ms in my benchmark, down from minutes.

**The cause:** for every incoming contact, the old code scanned the whole result with `findIndex` and re-normalized every existing email on each comparison. That is roughly 30k × 50k normalizations.

**The change:** I index the existing contacts by normalized email in a `Map` once, then look up each incoming contact in O(1). Behavior is unchanged:
- The first existing entry with a given email is the one merged into.
- Incoming duplicates merge with each other in arrival order.
- New contacts are appended in arrival order.

**Verification:**
- `npm test`: 8/8 pass.
- `npm run typecheck`: clean.
- Benchmark: a scratch script (since deleted) merged 50k existing with 30k incoming in 33.3 ms.

I did not benchmark the old code in this session, so the "minutes" figure is from your report. I did not change `csv.ts`, `pipeline.ts`, or `merge.ts`. If the import is still slow end to end, the CSV parsing or serialization is the next place to look.