`mergeContacts` now runs in about 37 ms on a 50k-row book with a 30k-row upload, down from about 53 seconds. The fix is in `src/import.ts`, and I haven't committed it.

**The cause:** for each incoming contact, `findIndex` scanned the whole result list and normalized every email in it. That is roughly 1.5 billion normalizations at your scale.

**The fix:** I build a `Map` from normalized email to position once, before the loop. Each incoming contact is then a single lookup. New contacts are added to the map as they are appended, so duplicates within the upload still merge with each other. If `existing` already contains duplicate emails, the map keeps the first one, the same as `findIndex` did.

**Verification:**
- `npm test`: all 8 tests pass.
- `npm run typecheck`: clean.
- Benchmark: 50k existing plus 30k incoming, timed before and after the change with the same input. Before: 52,796 ms. After: 37 ms. Both produce 55,000 rows. I deleted the temporary benchmark file afterwards.

Nothing else in the code was changed.