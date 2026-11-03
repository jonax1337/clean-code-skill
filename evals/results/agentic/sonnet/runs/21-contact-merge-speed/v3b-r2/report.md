`mergeContacts` now takes about 25 ms for 30k incoming contacts against 50k existing, where before it took minutes. I didn't time the old version, so there's no measured before/after.

**Cause:** for every incoming contact, `findIndex` scanned the whole result list and re-normalized each entry's email. That is about 30k × 50k normalizations.

**Fix:** `src/import.ts` now builds a `Map` from normalized email to index once, then does an O(1) lookup per incoming contact. Newly appended contacts are added to the map, so duplicates within the upload still merge with each other.

**Behavior:** unchanged. If `existing` already holds the same email twice, the first entry still receives the merge, as `findIndex` did. I added a test for that case in `test/import.test.ts`.

**Checks:**
- `npm test`: 9 passed, 0 failed.
- `npm run typecheck`: no errors.
- The 25 ms comes from a throwaway script on synthetic data (50k existing, 30k incoming, half of them overlapping). I deleted the script afterwards.

I didn't change `mergeContact` or the CSV parsing, and I didn't profile them.