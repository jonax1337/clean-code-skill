`mergeContacts` in `src/import.ts` now finds duplicates with a map from normalized email to position, instead of scanning the whole list for every incoming contact. That scan did about 30k × 50k comparisons, and each one normalized both emails. It now runs in a single pass over both lists.

`npm test` passes (10 tests) and `npm run typecheck` reports no errors.

Results are the same as before:
- The first matching entry still receives the merge, including when the stored book already repeats an email.
- Duplicates within the upload still merge with each other.
- New contacts are still appended in arrival order, and `merge.ts` and `normalize.ts` are unchanged.

I added two tests to `test/import.test.ts`:
- **Repeated stored emails:** one checks that the first entry gets the merge when the stored list repeats an email.
- **Speed:** one merges 30k contacts into 50k and asserts it finishes in under a second. I didn't time the old version, and I didn't check how long the new one takes. The test only asserts the under-a-second limit, and it passes.

The speed test uses a wall-clock limit, so it could fail on a very slow CI machine. If that becomes a problem, drop that assertion.

I only touched `mergeContacts`. `pipeline.ts` also parses both CSVs on every upload, and I didn't look at that. If uploads are still slow, check it next.