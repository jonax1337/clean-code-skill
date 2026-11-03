`mergeContacts` is fixed: merging 30k contacts into a 50k book now takes about **26 ms** in a local benchmark with made-up contacts, down from minutes.

**Why it was slow:** for every incoming contact, `findIndex` scanned the whole result list and re-normalized every email on each comparison. That's roughly 30k × 50k+ comparisons, or more than 1.5 billion string normalizations.

**The fix** (`src/import.ts`): before the loop, I normalize each existing email once and store it in a `Map` that points to its position in the list. Each incoming contact then needs one lookup instead of a full scan. New contacts are added to the map as they're appended, so duplicates within the same upload still merge with each other.

Results come out exactly as before:
- **Order:** existing entries stay in place and new ones are appended in arrival order.
- **Duplicates already in the book:** if the existing list has two entries with the same email, the first one gets the merge, just as `findIndex` did. I added a test in `test/import.test.ts` for this, since it's the one place a Map could easily have behaved differently.
- **Map stays valid:** `mergeContact` always keeps the stored entry's email, so a map entry can't go out of date after a merge.

All 9 tests pass and `tsc --noEmit` is clean. The benchmark was a throwaway script, and I deleted it afterwards. I haven't committed anything.