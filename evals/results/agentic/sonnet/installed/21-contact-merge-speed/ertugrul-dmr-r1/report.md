I rewrote `mergeContacts` in `src/import.ts` to look contacts up in a `Map`. I haven't run it or any tests.

**Cause:** for every incoming contact, it scanned the whole result with `findIndex` and normalized both emails each time. With 30k incoming contacts against 50k existing, that is on the order of a billion comparisons and normalizations.

**Fix:** it now builds a `Map` from normalized email to array index once, then does one lookup per incoming contact. Cost is now linear in the number of contacts.

**Behavior should be unchanged:**
- **First match wins:** if `existing` already has duplicate emails, the map keeps the first index, as `findIndex` did.
- **Duplicates within the CSV:** new contacts are added to the map as they are appended, so a repeated email later in the same upload merges into the earlier one.
- **Stable key:** `mergeContact` keeps the existing record's email, so the map key never goes stale after a merge.
- **Order:** output order is the same.