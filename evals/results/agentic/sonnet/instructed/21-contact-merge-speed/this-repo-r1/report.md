`mergeContacts` in `src/import.ts` now runs in linear time instead of quadratic. The old code scanned the whole result list for every incoming contact and re-normalized every email on each scan. For 30k incoming contacts against 50k existing, that was billions of comparisons.

The new version builds a `Map` from each normalized email to its index in the result list. Each incoming contact is then one lookup, and new contacts are added to the map as they're appended. This keeps the old behavior:
- **Duplicates in the existing book:** the first entry receives the merge.
- **Duplicates within the upload:** they merge into the contact the upload added first.
- **Order:** new contacts are appended in arrival order.

I added one test for the existing-duplicates case, since the old tests didn't cover it. `npm test` passes 9 of 9 and `npm run typecheck` ran without errors. I didn't time it on a 30k/50k file, so the speedup is from the algorithm change, not a measurement.