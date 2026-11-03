I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole list for every incoming contact. I haven't run it or any tests, so the speedup is untimed.

The old code called `findIndex` on the growing result for each incoming contact and normalized both emails every time. At 30k incoming against 50k existing, that is on the order of a billion comparisons and normalizations. It now builds a `Map` from normalized email to position once and looks each contact up in constant time. New contacts are added to the map as they're appended, so duplicates within the CSV itself still merge.

Behavior should be unchanged:
- **Order:** results come out in the same order as before.
- **Duplicate emails in the existing list:** the first one wins, as `findIndex` did.
- **Positions stay valid:** `mergeContact` keeps the existing email, so a merged contact's map entry never goes stale.