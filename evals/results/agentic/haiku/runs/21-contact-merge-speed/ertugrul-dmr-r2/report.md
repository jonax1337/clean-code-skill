`mergeContacts` now runs in about 33 ms for 30k incoming contacts into a 50k book, down from minutes. The tests and typecheck pass.

**Cause:** For every incoming contact, the old code called `findIndex` over the whole growing result array and normalized the email on both sides at each step. That is roughly 30k × 50k string comparisons with repeated `trim().toLowerCase()` calls.

**Fix (`src/import.ts`):** Build a `Map` from normalized email to index once, then look up each incoming contact in O(1). Two details keep the behavior the same as before:
- If the existing book already has duplicate emails, the map keeps the first index, matching `findIndex`.
- Contacts appended from the incoming list are added to the map, so later duplicates in the same upload still merge into them.

The public signature and the merge semantics are unchanged. I did not benchmark the original code for a before/after comparison, so the "minutes" figure is your report, not something I measured. I did not commit anything.