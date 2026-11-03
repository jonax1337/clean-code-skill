`mergeContacts` is now linear instead of quadratic. On 50k existing plus 30k incoming contacts, it runs in about 39 ms.

**The cause:** for every incoming contact, `findIndex` scanned the whole result and normalized the email on each comparison. That is roughly 1.5 billion normalizations at your scale.

**The fix (`src/import.ts`):** I build a `Map` from normalized email to position once, before the loop. Each incoming contact is then a single lookup. New contacts are added to the map as they are appended, so duplicates inside the upload still merge with each other. For existing duplicates, the first occurrence wins, as before.

**Verification:**
- `npm test`: 8/8 pass.
- `npm run typecheck`: clean.
- I compared the new function with the original on 300 random inputs, including duplicates within and across both lists. The outputs were identical.
- Timing: 39 ms for 50k + 30k. I did not time the original at full scale, so I have no before number for your data.

The benchmark and equivalence script live in `%TEMP%\bench-import`, outside the repo. I did not change `pipeline.ts` or `csv.ts`. I only checked that `importCsv` calls `mergeContacts` directly, so any remaining slowness in CSV parsing or serialization would show up as a separate cost. I have not timed the full `importCsv` path.

I did not commit anything.