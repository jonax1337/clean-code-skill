`mergeContacts` is fast now. With 30k contacts merged into a 50k book, it dropped from about **42 s to about 21 ms** on this machine.

**Why it was slow:** for each incoming contact, the old code scanned the whole result list with `findIndex` and cleaned up (normalized) both emails on every comparison. That's about 30k × 50k+ comparisons, each doing two `trim().toLowerCase()` calls.

**The fix** (`src/import.ts`): the function now builds a lookup from cleaned-up email to list position once, before the loop. Each incoming contact is then a single lookup, and new contacts are added to the lookup as they're appended, so duplicates within the upload still merge with each other. The function's signature, the result order and the merge rules are unchanged.

**One behavior I kept on purpose:** if the stored book already has two entries with the same email, the old code always merged into the first one. The lookup only records the first position per email, so that still holds. I added a test for this to `test/import.test.ts` and ran it against the old code first, where it passed, so it confirms the behavior is the same.

**Checks I ran:**
- `npm test`: 9 passed, 0 failed (before and after the change)
- `npm run typecheck`: no errors
- A throwaway benchmark with 50k stored and 30k incoming contacts, half of them overlapping: 21 ms new, 41,980 ms old. I deleted the script afterwards.

Nothing is committed yet.