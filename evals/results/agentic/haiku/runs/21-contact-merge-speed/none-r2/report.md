`mergeContacts` is now fast. On a synthetic run with 50k existing and 30k incoming contacts, it dropped from **86 s to 34 ms**, and the output is identical.

**The cause:** for every incoming contact, `findIndex` scanned the whole result array and re-ran `normalizeEmail` on each entry. That's roughly 50k × 30k comparisons with string work each time.

**The fix** (`src/import.ts`): I build a `Map` from normalized email to index once, up front, and look each incoming contact up in it. Behavior is unchanged:
- Matching is still first-match and still uses `normalizeEmail`, so case and whitespace are handled as before.
- New contacts are added to the map as they're appended, so duplicates within the incoming list still merge with each other.
- Merged entries keep their email, so their map keys stay valid.

**Verification:**
- `npm test`: all 8 tests pass.
- `tsc --noEmit`: exit 0.
- Benchmark: the old version was timed from `git show HEAD:src/import.ts` on the same data.

I haven't changed anything else, and the change isn't committed. I only timed `mergeContacts`. The real upload also goes through `parseContactsCsv` in `src/csv.ts` (called from `src/pipeline.ts`), which I didn't profile. If the upload is still slow after this change, that's the next place to look. I can check it with a timing run on a real CSV.