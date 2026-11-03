`mergeContacts` now takes about 33 ms for 30k incoming contacts against 50k existing ones, down from minutes. I timed that with a throwaway script on synthetic data and deleted the script afterwards.

**Cause:** the old code ran `findIndex` over the whole result list for every incoming contact. That is O(n·m), and each comparison normalized the email again.

**Fix** (`src/import.ts`): the function builds a `Map` from normalized email to list position once, then looks up each incoming contact in it. The behavior is the same as before:
- If the existing list already repeats an email, the merge goes into the first entry, as `findIndex` did.
- Duplicates inside the incoming list merge with each other.
- Order and the `mergeContact` semantics are unchanged.
- The signature is unchanged.

**Test:** I added one test for the repeated-email case, `test/import.test.ts`, since the old tests didn't cover it.

`npm test` passes (9 tests) and `tsc --noEmit` reports no errors.

I didn't touch the rest of the upload path (`csv.ts`, `pipeline.ts`). I only looked at `mergeContacts`, so I can't say whether anything else on that path is slow.