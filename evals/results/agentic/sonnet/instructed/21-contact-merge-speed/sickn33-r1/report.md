I rewrote `mergeContacts` in `src/import.ts` to look contacts up in a map instead of scanning the list. I haven't run it or any tests.

**Cause:** for every incoming contact, `findIndex` walked the whole result list and normalized both emails each time. With 30k incoming contacts against 50k existing, that's over a billion normalizations.

**Fix:** it now builds a `Map` from normalized email to position once, up front. Each incoming contact is a single lookup, and new contacts are added to the map as they're appended. The cost is now proportional to the number of contacts instead of their product.

**Behavior is unchanged:**
- **Duplicates in the existing list:** a repeated email still merges into the first entry, because the map keeps the first position for each email.
- **Duplicates within the upload:** they still merge into the entry appended earlier.
- **Order:** it is the same as before.
- **Stale positions:** `mergeContact` never changes the email, so the stored positions stay valid.