I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole list for every incoming contact. I haven't run it or any tests.

**Cause:** for each incoming contact, `findIndex` walked the whole result list and normalized both emails on every comparison. With 30k incoming contacts against 50k existing, that is about a billion normalizations.

**Fix:** it now builds a `Map` from normalized email to array position once, then does a constant-time lookup per incoming contact. New contacts are added to the map as they're appended. As a result, duplicates within the CSV itself merge into each other, as before.

**Behavior preserved:**
- If the existing list has duplicate emails, the first one still wins, as it did with `findIndex`.
- Output order is unchanged.
- `mergeContact` keeps the existing entry's `email`, so the map keys never go stale after a merge.

I also added a small helper, `indexFirstOccurrences`, that builds the initial map. That follows the skill's rule that a function should do one thing (G30).