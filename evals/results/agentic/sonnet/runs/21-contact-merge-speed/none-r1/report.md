I rewrote `mergeContacts` in `src/import.ts` so each incoming contact is found with a map lookup instead of a scan of the whole address book. The 8 existing tests pass. I didn't time it on a 30k-into-50k import, so I haven't measured the speedup.

**Cause:** the old code ran `findIndex` over the result for every incoming contact, and each pass re-normalized every existing email. That is roughly 30k × 50k normalizations.

**Fix:** the function now builds a `Map` from normalized email to index once, then does a constant-time lookup per incoming contact. New contacts are added to the map as they're appended, so duplicates within the upload still merge with each other.

**Behavior:** it is unchanged. If the existing book already has two entries with the same email, the contact merges into the first one, as before. Output order is the same too.