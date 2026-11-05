`mergeContacts` is now fast: merging 30k contacts into 50k takes about 68 ms in the new test.

**Why it was slow:** for every incoming contact, `findIndex` scanned the whole result list and normalized both emails each time. At your sizes that's well over a billion string operations.

**Fix (`src/import.ts`):** the function now builds a map from normalized email to position once, so each lookup is instant. Each email is normalized only once. Contacts added during the import go into the map too, so duplicates within the CSV still get merged with each other. If the existing book already has two entries with the same email, the map points to the first one, so the merge still goes into the same entry as before. The output is identical to before, including order.

**Tests (`test/import.test.ts`):**
- A test that, when the existing book has duplicates, the merge goes into the first matching entry.
- A test at your scale (30k into 50k, 15k overlapping): it checks the result count and order and fails if the merge takes longer than 2 s.

All 10 tests pass (`npm test`), and `npm run typecheck` ran with no errors.