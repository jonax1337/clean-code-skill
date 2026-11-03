`mergeContacts` is now fast. On synthetic data matching your numbers (50k existing contacts, 30k incoming, half of them duplicates), it went from about **35 s to about 27 ms**.

**Why it was slow:** for every incoming contact, the old code searched the whole result list and normalized both emails at every step. That's roughly 30k × 65k email comparisons, each one doing a trim and lowercase twice.

**The fix** (`src/import.ts`): before the loop, the function builds a lookup table from normalized email to position in the list. Each incoming contact is then matched with a single lookup, and new contacts are added to the table as they're appended. That keeps the existing behaviour where duplicates within the upload merge with each other.

One edge case needed care. If your address book already contains two entries with the same email, the old code always merged into the first one. The table only records the first occurrence, so that still holds. I added a regression test for it in `test/import.test.ts`.

**Verification:**
- `npm test`: 9 passed, 0 failed.
- `npm run typecheck`: ran with no errors.
- The timings come from a throwaway script I ran against both the old and new versions; I deleted it afterwards.

I didn't commit anything; the changes are in your working tree.