I rewrote `mergeContacts` in `src/import.ts` to look up emails in a map instead of scanning the whole list. The existing tests and the typecheck pass. I didn't time it on a 30k-into-50k import, so the speedup is unmeasured.

**Cause:** for every incoming contact it ran `findIndex` over the whole result and normalized the email of every entry on each pass. That is roughly 30k × 50k comparisons, each with two string normalizations.

**Fix:** it now builds a `Map` from normalized email to index once, then does one lookup per incoming contact. Each email is normalized once, so the work grows linearly with the data instead of quadratically.

**Behavior:** it should be unchanged.
- If the existing book already has duplicate emails, a match merges into the first one, as `findIndex` did.
- A newly appended contact is added to the map, so later duplicates within the same upload merge into it.
- Output order is the same.

I didn't add a new test. The existing ones already cover merging into existing entries, case and whitespace differences, and duplicates within the upload.