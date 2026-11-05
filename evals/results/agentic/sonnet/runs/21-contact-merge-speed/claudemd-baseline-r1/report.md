`mergeContacts` in `src/import.ts` no longer scans the whole list for every incoming contact. It now builds a map of normalized email to position once, then looks each contact up in constant time. That changes the work from roughly 30k × 50k email comparisons to about 80k lookups.

Results are the same as before:
- A contact whose email is already present is merged into the first entry with that email.
- New contacts are appended in the order they arrive.
- Duplicates within the incoming list merge into each other.

I added two tests in `test/import.test.ts`. One checks that when the existing list already has duplicate emails, the first entry gets the merge. The other merges 30k contacts into 50k and asserts it finishes in under 2 seconds. I didn't time the old version, so I haven't measured the speedup. The full suite passes (10 of 10) and `tsc --noEmit` reports no errors.

If a CSV upload is still slow after this, the time is somewhere other than `mergeContacts`, for example in parsing.