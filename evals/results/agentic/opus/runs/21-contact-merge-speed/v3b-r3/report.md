`mergeContacts` is now fast. Merging 30k contacts into a 50k book took **83 s before and 37 ms after**, about 2,000× faster.

**Why it was slow:** for every incoming contact, it scanned the whole result list with `findIndex` and re-normalized both emails at each step. That's roughly 2 billion `trim().toLowerCase()` calls for an upload your size.

**The fix (`src/import.ts`):** the function now builds a `Map` from normalized email to position once, then looks each incoming contact up in it. New contacts are added to the map as they're appended, so duplicates within the same upload still merge with each other. The result and the function signature are unchanged.

There's one edge case I kept on purpose. If the address book already holds two entries with the same email, the old code merged into the first one, and the map does the same. I added a test for this to `test/import.test.ts` and checked that it passes against the original code before changing anything.

**Checks:**
- `npm test`: 9 passed, 0 failed
- `npm run typecheck`: clean
- The benchmark used a throwaway script with synthetic data (50k existing, 30k incoming, 15k overlapping), run against both the old and new code. I deleted it afterwards.

I didn't commit anything.