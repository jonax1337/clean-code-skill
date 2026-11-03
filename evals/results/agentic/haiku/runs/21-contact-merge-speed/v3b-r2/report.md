`mergeContacts` is now linear instead of quadratic. The 30k-into-50k merge takes about 80 ms in the new test, down from minutes.

**What was wrong:** For every incoming contact, `findIndex` scanned the whole result list and called `normalizeEmail` on each entry. That is roughly 30,000 × 50,000 normalizations per upload.

**The fix** (`src/import.ts`): build a map from normalized email to index once, then look up each incoming contact in O(1). Merge and append behavior is unchanged:
- If `existing` has duplicate emails, the first one still wins.
- Duplicates within the incoming batch still merge into the entry appended earlier in the same call.

**Test added** (`test/import.test.ts`): a scale test that merges 30k incoming into a 50k book and asserts a 2-second ceiling. The length check is 55,000: 25k incoming emails match existing ones and 5k are new. The test ran fine on the first attempt, but my first draft expected 50,000 and failed. That was my arithmetic error, which I corrected.

**Results:**
- `npm test`: 9 passed, 0 failed.
- `npm run typecheck`: no errors printed. I piped it through `tail`, so the exit code I printed is `tail`'s, not `tsc`'s.

I did not profile the rest of the pipeline (CSV parsing, `storedCsv` re-serialization in `src/pipeline.ts`). If the upload is still slow after this, those are the next places to look. I did not run it against a real CSV.