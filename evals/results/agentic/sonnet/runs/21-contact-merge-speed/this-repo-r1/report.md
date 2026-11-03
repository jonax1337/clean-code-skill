`mergeContacts` now takes about 79 ms for 30k incoming contacts into 50k existing, down from minutes. I measured that with a throwaway script, not as a committed benchmark.

**Cause:** for every incoming contact, `findIndex` scanned the whole result and normalized both emails on each comparison. That is roughly 30k × 50k comparisons, each with two string allocations.

**Fix, in `src/import.ts`:** the function now builds a `Map` from normalized email to index once. After that, each incoming contact costs one lookup. New contacts are registered in the map as they are appended, so duplicates inside the upload still merge with each other.

**Behavior preserved:** if the existing book already holds two contacts with the same email, the first one still receives the merge, as it did with `findIndex`. I added a test for that case in `test/import.test.ts`.

**Checks:** `npm test` passes (9 tests, 0 failures) and `npm run typecheck` is clean.

I didn't touch anything else. The surrounding pipeline (`csv.ts`, `pipeline.ts`) wasn't profiled, so any remaining slowness there is unchecked.