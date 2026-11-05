I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole list for every incoming contact. The old `findIndex` ran `normalizeEmail` on every existing entry for each of the 30k contacts, which is about 1.5 billion comparisons against 50k. It now builds a map from normalized email to position once and looks each contact up in it, so the work grows with the list size instead of with list size times upload size.

Behaviour is unchanged:
- **Duplicate emails in the existing book:** the first one still wins, as with `findIndex`.
- **Repeats inside the upload:** they still merge into the entry added earlier.
- **Merging:** `mergeContact` keeps the current email, so the map stays correct after a merge.

All 8 existing tests pass and the typecheck is clean. I didn't time it on a 30k-into-50k import, so the speedup is untested.