I've made `mergeContacts` in `src/import.ts` fast. On a test run with 30k contacts imported into a book of 50k, it went from **about 46 seconds to about 23 ms**.

**Why it was slow:** for every incoming contact, it searched the whole result list from the start, normalizing both emails on every comparison. That added up to about 1.5–3 billion string operations.

**The fix:** it now builds a lookup table once, mapping each normalized email to its position in the list. Each incoming contact is found with a single lookup, and newly added contacts go into the table too, so duplicates within the same upload still get merged with each other.

The results are the same as before:
- New contacts are still added in the order they arrive.
- If the existing book already has several entries with the same email, the merge still goes into the first one, as it did before.
- Positions in the table can't go stale, because merging two contacts always keeps the existing entry's email (`mergeContact` in `src/merge.ts`).

All 8 tests pass and the typecheck is clean. I haven't committed the change.