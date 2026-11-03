`mergeContacts` now takes about 30 ms for your case instead of about 51 seconds.

**Why it was slow:** for every incoming contact, the old code searched the whole result list with `findIndex` and normalized both emails at every comparison. With 30k incoming contacts against 50k existing ones, that's roughly 1.5 billion comparisons, each doing `trim().toLowerCase()` twice.

**The fix** (`src/import.ts`): I build a `Map` from normalized email to array index once, then each incoming contact is a single lookup. New contacts are added to the map as they're appended, so duplicates within the same upload still merge into each other. The behavior is otherwise unchanged:
- If the existing book already has two entries with the same email, the map stores the first one's index. An incoming match merges into that first entry, just as `findIndex` did.
- A merged entry keeps its original email (`mergeContact` doesn't change it), so its map entry stays correct.

**Test:** I added one to `test/import.test.ts` for the "duplicates already in the book" case, since no existing test covered it. It passed against the old code before I changed anything.

**Results:**
- `npm test`: 9 passed, 0 failed
- `npm run typecheck`: clean
- Benchmark (50k existing, 30k incoming, about half of them matches): **51,325 ms before, 31 ms after**. I ran it as a throwaway script and deleted it afterwards.

Nothing is committed yet.