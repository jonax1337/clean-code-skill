I rewrote `mergeContacts` in `src/import.ts` to build a `Map` from each normalized email to its position in the result. It builds that map once and does one lookup per incoming contact. The old code scanned the whole list with `findIndex` for every incoming contact, and normalized both emails on each comparison. That made the work grow with 30k × 50k comparisons. It now grows with 30k + 50k lookups.

The existing tests pass (8/8). I couldn't confirm that `tsc --noEmit` passed, because its output showed only npm notices and no result. I didn't time it on a 30k/50k dataset or add a benchmark.

Behavior should be unchanged, including two edge cases:
- If `existing` already contains duplicate emails, the first entry is still the one that gets merged into.
- Duplicates within the incoming list still merge with each other.

I didn't add a test for the duplicate-in-`existing` case.