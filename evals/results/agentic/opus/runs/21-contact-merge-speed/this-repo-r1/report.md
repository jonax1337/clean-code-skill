`mergeContacts` is fast now. On a synthetic run of 30,000 contacts merged into 50,000, it dropped from **67 s to 38 ms**, and both versions returned the same 55,000 contacts.

**Why it was slow:** for each incoming contact, the old code searched the whole result list with `findIndex` and re-normalized both emails at every step. At your sizes that's on the order of 1.5–2.5 billion comparisons.

**The fix** (`src/import.ts`): it now normalizes each existing email once and stores it in a lookup table (`Map`) of email → position. Each incoming contact is then a single lookup, and new contacts are added to the table as they're appended. The total work grows with the number of contacts rather than their product. The function's signature and output are unchanged.

**Behavior I kept on purpose:** if the stored book already has two entries with the same email, the old code merged into the first one. The table keeps the first position, so that still happens. I added a test for this in `test/import.test.ts` and ran it against the old code first to confirm it captures what the code did before.

**Checks:**
- `npm test`: 9 passed, 0 failed
- `npm run typecheck`: no errors
- The benchmark was a temporary script with generated data (not your real CSV), and I deleted it afterwards. I didn't add a timing test to the suite because those tend to fail randomly on slower machines.

I didn't touch `src/pipeline.ts`. If uploads still feel slow, the CSV parsing (`parseContactsCsv`) is the next thing to measure, but I haven't profiled it.