`mergeContacts` is now linear instead of quadratic. A 30k-into-50k import should take tens of milliseconds, not minutes.

**The cause:** for each incoming contact, `findIndex` scanned the whole result array and re-normalized every existing email on each comparison. That is roughly 1.5 billion string normalizations at your scale.

**The fix** (`src/import.ts`): I build a `Map` from normalized email to index once up front, then do a constant-time lookup per incoming contact. New contacts get registered in the map as they are appended, so duplicates within the upload still merge with each other. When the existing book already has duplicate emails, the map keeps the first entry, matching what `findIndex` returned before.

**Verification:**
- `npm test`: all 8 tests pass.
- `tsc --noEmit`: exit 0.
- Benchmark at full size (50k existing, 30k incoming): about 48 ms.
- Old and new implementations produce identical output on a 5k × 3k subset. The old version took about 813 ms on that subset alone, which is why I didn't time it at full size.

I didn't add tests, since the existing ones already cover the merge semantics. I also didn't commit anything. The only change in the repo is `src/import.ts`.