`mergeContacts` is now fast: on a test run of 30k contacts into a 50k book (15k of them already in the book), it went from about **82 seconds to 37 ms**.

**What was slow:** for every incoming contact, the old code searched the whole address book with `findIndex` and normalized both emails at every step. That's roughly 30k × 65k email comparisons per upload.

**The fix** (`src/import.ts`): it now builds a lookup from normalized email to position in one pass, then finds each incoming contact in constant time. New contacts are added to the lookup as they're appended, so duplicates within the same CSV still merge with each other. The results are exactly the same as before, including one edge case: if the existing book already has the same email twice, the merge still goes into the first one, as `findIndex` did. I added a test in `test/import.test.ts` to lock that in.

**Checks:** all 9 tests pass (the 8 existing ones plus the new one), and `tsc --noEmit` reports no errors. The timings came from a throwaway benchmark script, which I deleted afterwards. I haven't measured a real upload end to end, so if CSV parsing or saving is also slow, that would now be the next thing to look at.

Nothing is committed yet.