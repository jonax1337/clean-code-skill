I rewrote `mergeContacts` in `src/import.ts` so it no longer rescans the whole list for every incoming contact. I haven't run it or any tests.

**Cause:** the old code called `findIndex` over the result for each incoming row and normalized every entry's email each time. That is roughly 30k × 50k email normalizations, which is why imports took minutes.

**Fix:** it now builds a `Map` from normalized email to index once, then looks up each incoming contact in constant time. New contacts are added to the map as they're appended. The work is now proportional to the number of contacts, not their product.

**Behavior should be unchanged:**
- If the existing list already has duplicate emails, the first one still wins, as `findIndex` did.
- Duplicates within the incoming CSV still merge into the entry added earlier.
- Output order is the same.
- `mergeContact` keeps the existing record's email, so the stored indexes stay valid after a merge.