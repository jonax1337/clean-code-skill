`mergeContacts` is now linear instead of quadratic, so the 30k-into-50k import should take milliseconds. On a synthetic 50k + 30k run it finishes in about 33 ms. I did not time the old version; at 1.5 billion comparisons it would take minutes, which matches what you saw.

**The change** (`src/import.ts`): the old code scanned the whole result array for every incoming contact and normalized both emails on each comparison. Now a `Map` from normalized email to index is built once from the existing contacts, and each incoming contact is a single lookup. New contacts are added to the map as they are appended, so duplicates within the upload still merge with each other.

**Behavior is unchanged:**
- Existing duplicates still resolve to the first matching entry, as `findIndex` did.
- `mergeContact` keeps the existing entry's `email`, so each entry's map key stays valid after a merge.
- Output order is the same: existing entries in place, new ones appended in arrival order.

**Verification:** `npm test` passes all 8 tests, and `npm run typecheck` is clean. The benchmark script was a temporary file outside the repo and I deleted it.

**Not touched:** the CSV parsing and serialization in `src/csv.ts` run on every upload too. I didn't profile them, since you pointed at `mergeContacts`. If the import is still slow after this, that's the next place to look. I haven't committed anything.