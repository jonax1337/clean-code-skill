I made `mergeContacts` fast. On a test with 50k existing contacts and 30k incoming, it went from **53 s to about 50 ms**.

**Why it was slow:** for every incoming contact, the old code searched the whole result list with `findIndex` and normalized both emails on every comparison. That added up to about 1.5 billion comparisons and 3 billion `normalizeEmail` calls.

**The fix** (`src/import.ts`): the function now builds a `Map` from each normalized email to its position in the result, once at the start. Each incoming contact is then a single lookup. New contacts are added to the map as they're appended, so duplicates within the same upload still merge into each other.

The results are the same as before, including one edge case: if the address book already contains two entries with the same email, the merge still goes into the first one, as `findIndex` did.

**Tests** (`test/import.test.ts`), two added:
- A test for that duplicate-entries edge case. It passes on both the old and new code, so the behavior is unchanged.
- A timing test at your size (50k + 30k) with a 1 s limit. It fails on the old code (53,006 ms) and passes on the new one (about 50 ms). Timing tests can be flaky on slow CI machines; the 1 s limit leaves about 20× headroom, but you can drop the test if you'd rather not have one.

**Commands run:**
- `npm test`: 10 passed, 0 failed
- `npm run typecheck`: no errors

I haven't committed anything.