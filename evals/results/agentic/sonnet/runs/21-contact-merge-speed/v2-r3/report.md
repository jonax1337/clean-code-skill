I rewrote `mergeContacts` in `src/import.ts` to use a `Map` from normalized email to position in the result. The old version scanned the whole result list for every incoming contact, normalizing both emails each time. With 30k incoming contacts and about 50k existing, that was roughly a billion comparisons. The new version does one pass over the existing contacts to build the map, then one lookup per incoming contact, so the work grows linearly.

Behavior is the same as before:
- If the existing list already has duplicate emails, the first one still gets the merge, as `findIndex` did.
- Duplicates inside the upload still merge into the entry that was appended earlier.
- Output order is unchanged.

The 8 existing tests pass and the typecheck is clean. I didn't time it on a 30k-row import, so I haven't measured the speedup.

I didn't look at `csv.ts` or `pipeline.ts`. You said the time goes into `mergeContacts`, so I left them alone.