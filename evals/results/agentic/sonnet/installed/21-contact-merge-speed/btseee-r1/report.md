I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole list for every incoming contact. I haven't run it or any tests, and I haven't timed it on a large import.

**Cause:** each incoming contact ran `findIndex` over the result list and normalized every entry's email again. With 30k incoming contacts and 50k existing, that is roughly 1.5 billion email normalizations.

**Fix:** it now builds a `Map` from normalized email to list position once. After that, each incoming contact is a single lookup, so the work grows with the size of the lists instead of their product.

Behaviour should be unchanged:
- **Duplicates in the existing list:** an incoming contact still merges into the first match, as `findIndex` did.
- **Duplicates within the upload:** a second contact with the same email in one CSV still merges into the first, because newly appended contacts are added to the map.
- **Output order:** unchanged. `mergeContact` keeps the existing email, so the map keys stay valid after a merge.