I rewrote `mergeContacts` in `src/import.ts` so it no longer rescans the whole list for every incoming contact. I haven't run it or any tests, and I didn't time it on a large import.

**Cause:** the old code called `findIndex` over the result for each incoming contact, and each comparison normalized both emails again. With 30k incoming contacts against 50k existing, that is on the order of a billion normalizations.

**Fix:** it now builds a `Map` from normalized email to position once, then looks each incoming contact up in constant time. That makes the work roughly linear in the number of contacts. Each email is normalized once.

**Behavior:** the output should be the same as before.
- **Duplicates in the existing list:** the first entry still wins, as `findIndex` did.
- **Duplicates within the CSV:** a new contact is added to the map when it's appended, so a later row with the same email still merges into it.
- **Ordering:** order is unchanged.
- **Email field:** `mergeContact` keeps the existing record's `email`, so the map's keys stay valid after a merge.

This follows G5/G25-style cleanup only loosely; there was nothing else to clean in the file.