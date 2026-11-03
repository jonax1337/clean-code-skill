I rewrote `mergeContacts` in `src/import.ts` to look contacts up in a `Map` instead of scanning the whole list for each one. The existing tests pass and the typecheck is clean. I didn't time it on a 30k-into-50k import.

**Cause:** the old code ran `findIndex` for every incoming contact and normalized every existing email each time. That is roughly 30k × 50k normalizations, around 1.5 billion.

**Change:** the function now builds a normalized-email → index map once. Each incoming contact is then an O(1) lookup, and a new contact is added to the map when it's appended. The cost is now proportional to 80k contacts instead of 30k × 50k.

**Behavior is unchanged:**
- If the existing list already holds duplicate emails, a match still goes to the first one, as `findIndex` did.
- Duplicates inside the upload still merge with each other.
- Output order is the same.
- Merging keeps the existing entry's email, so the map's keys stay valid.

I didn't add a performance test.