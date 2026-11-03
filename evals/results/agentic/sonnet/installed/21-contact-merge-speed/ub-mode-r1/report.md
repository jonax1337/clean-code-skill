I rewrote `mergeContacts` in `src/import.ts` to look contacts up in a map instead of scanning the whole list for each one. I haven't run it or any tests, and I haven't timed it on a large import.

Before, every incoming contact scanned the result list and re-normalized every entry's email. For 30k contacts into 50k that is billions of operations. Now it builds a map from normalized email to position once, then does one map lookup per incoming contact. The work grows with the size of the lists rather than with their product.

Results should be the same as before:
- **Duplicate emails in the existing list:** the first one is still the one that gets merged, as with `findIndex`.
- **Duplicates within the upload:** a contact added from the upload is registered in the map, so a later row with the same email merges into it.
- **Merged emails:** `mergeContact` keeps the existing record's email, so the map keys stay valid after a merge.
- **Order:** new contacts are still appended in the order they arrive.