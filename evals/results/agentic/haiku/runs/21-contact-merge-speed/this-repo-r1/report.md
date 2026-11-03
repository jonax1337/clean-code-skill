`mergeContacts` is now fast. On a 50k-contact book merged with 30k incoming rows, it dropped from about 103 s to about 47 ms, and the output is identical to the old version.

**Cause:** for every incoming row, `findIndex` scanned the whole result and re-normalized every existing email, so the cost was O(n·m) with repeated work.

**Fix (`src/import.ts`):** I build a `Map` from normalized email to position once, then each incoming row is a single lookup. Newly appended contacts are added to the map, so duplicates within the upload still merge with each other. When the existing book already has duplicate emails, the first entry still wins, as before.

**Test (`test/import.test.ts`):** I added one test that pins the first-entry-wins rule, since that is the behavior the index could most easily break.

**Verification:**
- `npm test`: 9 pass, 0 fail (8 before, plus the new test).
- `npm run typecheck`: exits 0.
- Benchmark (scratch copy outside the repo, not committed): old 103,098 ms, new 47 ms, same 55,000-row output as JSON.

I did not touch `csv.ts`, parsing, or the summary code, since the timing was all in `mergeContacts`. I have not committed anything.