`mergeContacts` is fast now. On a synthetic run with 50k existing contacts and 30k incoming, it went from **87.5 s to 39 ms**.

**What was slow:** for every incoming contact, the old code searched the whole result list and normalized both emails at every step. That's about 30k × 65k comparisons, each doing two `trim().toLowerCase()` calls.

**The fix** (`src/import.ts`): it builds a `Map` from normalized email to position in the list once, then each incoming contact is a single lookup. New contacts are added to the map as they're appended, so duplicates within the same upload still merge with each other.

The results are unchanged:
- New contacts are appended in the order they arrive.
- If the existing book already has two entries with the same email, the first one still receives the merge, as `findIndex` did before. I added a test for this case to `test/import.test.ts`, since it's the one place a careless map could have changed results.
- A merge never changes the stored email, so a contact's map entry stays correct after it's merged.

All 9 tests and the typecheck pass. I haven't committed anything.