`mergeContacts` is fixed: merging 30k incoming contacts into a 50k address book now takes **about 28 ms instead of about 44 seconds** on synthetic data. All 8 tests and the typecheck pass.

**Why it was slow:** for each incoming contact, `findIndex` scanned the whole growing list and cleaned up (trimmed and lower-cased) every email again for every comparison. At your sizes that's well over a billion string operations.

**The fix** (`src/import.ts`): I now build a lookup table once, from cleaned-up email to the contact's position in the list. Each incoming contact takes one lookup. Newly added contacts go into the table too, so duplicates within the same upload still merge with each other.

**Behavior is unchanged:**
- If the existing book already has several contacts with the same email, only the first one goes in the table, so merges hit the same entry `findIndex` used to find.
- A merged contact keeps its original email, so its table entry stays correct.
- Order and output are the same as before.

I benchmarked with a throwaway script in my temp folder and added nothing to the repo. Nothing is committed yet.