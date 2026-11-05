`mergeContacts` is fixed. On a 50k-contact book with a 30k upload, it dropped from **63 seconds to about 31 ms**.

**The cause:** for every incoming contact, `findIndex` scanned the whole result array and re-normalized every existing email. That's roughly 1.5 billion normalizations at that size.

**The fix** (`src/import.ts`, the only file changed): I build a `Map` from normalized email to index once, then each lookup is O(1). The behavior is unchanged:
- The first existing entry with a given email wins, matching the old `findIndex`.
- A merged contact keeps its original position and id.
- New contacts are added to the map as they're appended, so duplicates inside the upload still merge with each other.

**Verification:**
- `npm test`: 8/8 pass.
- `tsc --noEmit`: clean.
- I compared the old and new implementations on 2,000 random inputs with duplicates, including duplicates inside the existing book. The outputs matched in every case.

I ran the timing and comparison with throwaway scripts outside the repo and deleted them afterward. I did not add a new test, since the existing ones already cover the merge rules.