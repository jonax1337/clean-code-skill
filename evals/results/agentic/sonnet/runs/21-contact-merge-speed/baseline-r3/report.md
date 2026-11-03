I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole list for every incoming contact. I haven't run it or any tests.

The old code called `findIndex` over the result for each incoming contact and normalized both emails on every comparison. With 30k incoming contacts and 50k existing, that is on the order of a billion comparisons. The new code builds a `Map` from normalized email to position once, then looks up each incoming contact in the map. That makes the whole merge roughly linear.

Behavior should be the same as before:
- If the existing list already has duplicate emails, the first one is still the one that gets merged into.
- Duplicates within the incoming file merge into the entry just added, as before.
- The map stays correct after merges because `mergeContact` keeps the existing contact's email.
- Output order is unchanged.