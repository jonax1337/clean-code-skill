`mergeContacts` now does 30k incoming contacts into 50k existing ones in about 70 ms. The 10 tests pass and `tsc --noEmit` reports no errors.

The slowness came from `findIndex` rescanning the whole result list for every incoming contact. It also re-normalized every stored email each time, which is quadratic work. I replaced it with a `Map` from normalized email to index in `src/import.ts`, built once up front. Results are the same as before:
- **Duplicate emails in the existing list:** an incoming contact still merges into the first entry, because the map only keeps the first occurrence.
- **Duplicates within the incoming list:** they still merge with each other, because new entries are added to the map as they are appended.
- **Signature and order:** unchanged.

I added two tests to `test/import.test.ts`:
- **First-match merge:** this covers the duplicate-emails case above.
- **Timing check:** it runs the 30k-into-50k import and asserts it finishes in under 2 seconds. That limit is loose (the run took about 70 ms), but timing tests can still be flaky on slow CI, so drop it if that's a concern.

I didn't profile the rest of the upload path (CSV parsing in `src/csv.ts` and `src/pipeline.ts`). Your profiling put the time in `mergeContacts`, so I left those alone.