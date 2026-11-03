I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole address book for every incoming contact. The tests pass and the typecheck is clean. I didn't time it on a 30k-into-50k import, so I haven't measured the speedup.

**Cause:** for each incoming contact, `findIndex` re-normalized every existing email. That is about 30k × 50k comparisons, each with a `trim().toLowerCase()`, which is where the minutes went.

**Fix:** the function now builds a `Map` from normalized email to position once, then does a constant-time lookup per incoming contact. It is roughly linear in the combined size instead of quadratic. New contacts are added to the map as they're appended, so duplicates within the upload still merge with each other.

Behavior is unchanged:
- If the existing book already has two entries with the same email, merges still go to the first one, as `findIndex` did.
- A merge never changes an entry's email, so the map stays valid.
- Output order is the same.