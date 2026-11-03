I rewrote `mergeContacts` in `src/import.ts` to look contacts up in a `Map` keyed by normalized email, instead of scanning the whole result list for every incoming contact.

The old version called `normalizeEmail` on every entry for every incoming contact, which is about 30k × 50k comparisons. The new version builds the map once and then does one lookup per incoming contact, so the cost grows linearly with the list size.

Behavior should be unchanged:
- **Duplicates already in the stored book:** the first occurrence wins, as `findIndex` did before.
- **Duplicates inside the upload:** newly appended contacts go into the map, so a later duplicate still merges into the first one.
- **Order:** merged and appended contacts end up in the same order as before.

`npm test` passes (8 of 8) and `npm run typecheck` is clean. I didn't time it on a 30k-into-50k import, so I haven't measured the speedup. I also didn't add a test, because the existing import tests already cover merging, case and whitespace handling, and duplicates within an upload.