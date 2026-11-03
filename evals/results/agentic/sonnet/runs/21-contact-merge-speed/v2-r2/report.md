I rewrote `mergeContacts` in `src/import.ts` so it's no longer quadratic. The existing tests and the typecheck pass, but I didn't time it on a 30k-into-50k import.

**Cause:** for every incoming contact, it ran `findIndex` over the whole result list and normalized every entry's email each time. That is about 30k × 50k comparisons, each with a `trim().toLowerCase()`.

**Fix:** the function now builds a `Map` from normalized email to index once, then does a constant-time lookup per incoming contact. Appended contacts are added to the map, so duplicates inside the upload still merge with each other.

**Behavior unchanged:**
- If `existing` already holds duplicate emails, the first one still wins, as `findIndex` did.
- Output order is the same.
- `mergeContact` is untouched, and it keeps the existing entry's email, so the map keys stay valid.

I didn't check `csv.ts` or `pipeline.ts`. If an import is still slow after this, I'd look there next.