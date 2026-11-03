`mergeContacts` is fast now. On a synthetic run (50k existing contacts, 30k incoming, 15k of them overlapping) it went from **76.5 s to 45 ms**.

**Why it was slow:** for each incoming contact, the old code searched the whole result list with `findIndex` and called `normalizeEmail` twice on every comparison. With your sizes that is billions of string operations.

**Fix (`src/import.ts`):** the function now builds a `Map` from normalized email to position in the result list once. Each incoming contact is a single lookup, and new contacts are added to the map as they are appended, so duplicates within the same upload still merge with each other. The function signature and output order are unchanged.

**One case I kept on purpose:** if the stored address book already has two entries with the same email, the old code merged into the first one. The map keeps only the first position per email, so that still happens. I added a test for this (`test/import.test.ts`) and ran it against the original code before changing anything, so it shows the behavior is the same.

**Checks:**
- `npm test`: 9 passed, 0 failed.
- `npm run typecheck`: no errors.
- The timing comparison used a throwaway script, which I deleted afterwards.

I didn't commit anything. The 45 ms covers only the merge. I didn't profile CSV parsing or anything else in `pipeline.ts`, so total upload time will depend on those too.