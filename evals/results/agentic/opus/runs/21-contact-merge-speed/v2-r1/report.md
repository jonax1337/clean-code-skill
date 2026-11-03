`mergeContacts` is now fast. On a synthetic run of 50k existing and 30k incoming contacts (15k overlapping), it took **83 s before and 37 ms after**.

**Why it was slow:** for every incoming contact, the old code searched the whole result list with `findIndex` and normalized both emails again on each comparison. That is about 30k × 50k+ comparisons, each doing two `trim().toLowerCase()` calls.

**The fix** (`src/import.ts`): the function now builds a `Map` from normalized email to index in the result list once. Each incoming contact then needs a single lookup, and new contacts are added to the map as they're appended. The results are the same as before:
- Order is unchanged: existing entries first, then new ones in the order they arrive.
- Duplicates within the upload still merge with each other.
- If the existing book already has several entries with the same normalized email, the map keeps the first one. That's the entry `findIndex` would have found, so the incoming record merges into the same place as before.
- `mergeContact` always keeps the current entry's email, so an entry's key never changes after it's stored.

**Checks:** `npm test` (8/8 pass) and `npm run typecheck` both pass. The benchmark was a throwaway script, and I deleted it afterwards. Nothing is committed yet.