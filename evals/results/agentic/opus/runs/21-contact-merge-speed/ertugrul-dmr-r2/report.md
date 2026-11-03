`mergeContacts` is now fast. On a synthetic run with 50k existing and 30k incoming contacts, it took **about 108 seconds before the change and about 48 ms after**.

**Why it was slow:** for every incoming contact, the old code scanned the entire result list and re-normalized both emails on each comparison. That's 30k × 50k+ string operations. The comparison count grows with the size of the book times the size of the upload.

**The fix** (`src/import.ts`): the function now normalizes each existing email once and builds a `Map` from normalized email to position in the list. Each incoming contact is then a single lookup. New contacts are added to the map as they're appended, so duplicates within the same upload still merge with each other.

**Behaviour is unchanged**, including one edge case the old code handled without saying so: if the existing book already holds two entries with the same normalized email, the incoming contact merges into the first one. The map keeps the first position it sees, which matches the old `findIndex`. I added a test for this case to `test/import.test.ts`. The lookup key also stays valid after a merge, because `mergeContact` always keeps the current entry's email.

**Verification:** `npm test` passes all 9 tests and `tsc --noEmit` is clean. The timings above come from a throwaway script outside the repo, using generated data with 15k overlapping emails, not a real CSV.

Clean Code notes: the "keep the first position" rule is in a small, named helper, `rememberFirstIndex`, so its purpose is clear (G16, G28). I added the test for the duplicate edge case, where a quiet behaviour change was most likely (T6).

The changes aren't committed. Let me know if you want me to commit them.