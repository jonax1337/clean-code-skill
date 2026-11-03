`mergeContacts` in `src/import.ts` no longer scans the whole list for every incoming contact. It now builds a map from normalized email to position once and looks each contact up in it. That takes the cost from roughly 30k × 50k email comparisons, each normalizing both sides, to about one pass over each list.

Behavior is unchanged:
- If the existing book already has duplicate emails, the first entry still wins.
- Duplicates inside the upload still merge into the first occurrence.
- Output order is the same.

`npm test` passes (8 of 8) and `npm run typecheck` reports no errors. I didn't benchmark a 30k/50k import, so I haven't measured the speedup. I also didn't add a test, because the existing tests already cover case and whitespace matching, duplicates within the upload, and field precedence.

I didn't look at `src/pipeline.ts` or `src/csv.ts`. If imports are still slow after this, check those next.