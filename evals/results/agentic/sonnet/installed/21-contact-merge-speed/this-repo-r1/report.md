I rewrote `mergeContacts` in `src/import.ts` so it no longer rescans the whole list for every incoming contact. I haven't run it or any tests, and I didn't time it on a large import.

**Cause:** for each incoming contact it ran `findIndex` over the whole result and called `normalizeEmail` on every entry it checked. That is O(existing × incoming), which for 30k into 50k means billions of normalizations.

**Fix:** it now builds a `Map` from normalized email to array index once, then looks up each incoming contact in constant time. Newly appended contacts are added to the map, so duplicates inside the CSV itself still merge.

**Behavior is unchanged:**
- If the existing list already has duplicate emails, the first one still wins, as `findIndex` did.
- Order is preserved.
- `mergeContact` keeps the existing contact's email, so the map keys stay valid after a merge.