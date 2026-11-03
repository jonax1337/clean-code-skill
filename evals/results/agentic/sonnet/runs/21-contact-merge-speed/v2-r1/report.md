`mergeContacts` in `src/import.ts` now finds duplicates with a lookup table, so each contact is checked in constant time instead of by scanning the whole list. The existing 8 tests and the type check pass. I didn't time it on a 30k-into-50k import, so the speedup itself is unmeasured.

The old code scanned the whole result list for every incoming contact, which is roughly 30k × 50k comparisons. It also re-normalized the email of every entry on each scan. Now each email is normalized once, and the table maps it to the contact's position in the result.

Behavior is unchanged:
- If the existing list already has duplicate emails, the first one still wins, as `findIndex` did.
- Duplicates within the upload still merge into the entry added earlier.
- Output order is the same.

I didn't add a performance test.