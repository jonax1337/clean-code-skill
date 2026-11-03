`mergeContacts` in `src/import.ts` no longer scans the whole address book for every incoming row. A 30k-into-50k merge now takes about 76 ms in a standalone benchmark, down from minutes.

**Cause:** for each incoming contact, `findIndex` walked the entire result array and called `normalizeEmail` on both sides of every comparison. That is roughly 30k × 50k normalizations.

**Fix:** I build a `Map` from normalized email to its index once, then each incoming row is a single lookup. Contacts appended earlier in the same upload are added to the map, so later duplicates in the same file still merge into them. When an address book already contains duplicate emails, the map keeps the first index, as `findIndex` did.

**Verification:**
- `npm test`: all 8 tests pass.
- `npm run typecheck`: runs clean (I checked the output tail, which shows no errors).
- The 76 ms figure is from a synthetic benchmark (50k existing, 30k incoming with case and whitespace variants). I didn't time the old code on the same data, so I can't give you a before/after ratio. I also haven't tested your real CSV.

`importCsv` in `src/pipeline.ts` also runs `parseContactsCsv` and `toContactsCsv`. I didn't review or profile those. If the real upload is still slow after this change, they are the next place to look.