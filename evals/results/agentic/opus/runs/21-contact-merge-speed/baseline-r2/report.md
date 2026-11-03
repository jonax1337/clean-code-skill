Merging 30k contacts into a 50k address book now takes about **30 ms**. Before, it took minutes.

**Why it was slow:** for each incoming contact, `mergeContacts` scanned the whole result list with `findIndex` and normalized every email along the way. That added up to billions of string operations for this size of import.

**The fix** (`src/import.ts`): the function now normalizes each email once and stores it in a `Map` that points to the contact's position in the list. Each incoming contact is then a single lookup. The behaviour hasn't changed:
- Existing contacts keep their order, and new ones are added at the end in the order they arrive.
- A contact whose email is already there is merged into the first entry with that email, as `findIndex` did. This still holds if the stored book already has duplicate emails.
- Duplicates within the upload are merged into each other, because each new contact goes into the map as soon as it's added.

**Checks:** all 8 tests pass and `tsc --noEmit` is clean. For the timing I ran a throwaway benchmark (50k existing, 30k incoming, 25k overlapping), which gave the expected 55,000 contacts in 29 ms.