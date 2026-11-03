`mergeContacts` is fast now. A synthetic run with your sizes (30k incoming merged into a 50k book) finishes in about 31 ms. All 9 tests pass and the type check is clean.

**Why it was slow:** for every incoming contact, the old code scanned the whole result list with `findIndex` and normalized both emails at each step. With your numbers that adds up to well over a billion string normalizations.

**What I changed** in `src/import.ts`:
- Before the loop, it builds a `Map` from each normalized email to its position in the list, so each lookup is instant instead of a full scan.
- When a new contact is appended, it goes into the map too, so duplicates within the same upload still merge with each other.
- If the address book already holds the same email twice, the merge still goes into the first one, as before. This works because `mergeContact` never changes the email, so the map stays correct.

**Test added:** a regression test in `test/import.test.ts` for the "same email twice in the book" case, so the first-entry rule can't change by accident.

Nothing is committed yet. Tell me if you want me to commit it.