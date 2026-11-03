`mergeContacts` is now about 2,900× faster on a 50k-into-30k merge: 82.9 s before, 28.7 ms after. The output is identical.

**The cause:** for each incoming contact, `findIndex` scanned the whole result array and re-normalized every existing email on every comparison. That is roughly 50k × 30k × 2 normalizations.

**The fix** (in `src/import.ts`, the only file changed): build a `Map` from normalized email to index once, up front, then do a constant-time lookup per incoming contact. Two details keep behavior the same:
- If the existing list already has duplicate emails, the map keeps the first index, as `findIndex` did.
- `mergeContact` keeps the current record's email, so the map key stays valid after a merge.

**Verification:**
- `npm test`: 8/8 pass, same as the baseline.
- `npm run typecheck`: passes.
- Benchmark: I ran the original (from `git show HEAD`) and the new version on the same input. Their outputs match exactly.

**Not done:**
- `pipeline.ts` calls `parseContactsCsv` on both files before the merge. I didn't profile the parser. If the upload is still slow after this change, that's the next place to look.
- The benchmark temp folder `C:\Users\Jonas\AppData\Local\Temp\bench-merge` is still on disk. Windows reports it as locked, so I couldn't delete it. It's outside the repo and safe to remove by hand.
- I didn't commit anything.