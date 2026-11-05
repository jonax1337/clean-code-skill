`mergeContacts` now does one hash lookup per incoming contact instead of scanning the whole address book, so the import should no longer take minutes. All 10 tests pass and typecheck is clean.

**The change (`src/import.ts`):** Before, each incoming row ran `findIndex` over the full result list and re-normalized every stored email. Now the function builds a `Map` from normalized email to position once, then looks up each incoming row in constant time. New contacts are added to the map as they are appended, so duplicates within the upload still merge. Merge results and ordering are the same as before.

**Tests (`test/import.test.ts`):**
- A regression test for the case where the stored book already has duplicate emails: an incoming row merges into the first match, as the old code did.
- A scale test with 50,000 stored contacts and 30,000 incoming rows (25,000 matches, 5,000 new). It checks the result length and the ordering at both ends. It ran in about 67 ms.

I did not benchmark the old code against the new, so I can't give you an exact speedup. The old cost was roughly 30k × 50k normalizations and comparisons, which fits minutes of work, but I haven't measured it. The rest of the import path (`parseContactsCsv` and `toContactsCsv`) I didn't touch or profile. If the real upload is still slow after this, those are the next places to look.

Nothing is committed.