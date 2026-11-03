`mergeContacts` now runs in about 50 ms at your scale, down from about 74 seconds, with the same output.

**The cause:** for every incoming contact, `findIndex` scanned the whole result list and re-normalized every existing email, so the work grew with incoming × existing (30k × 50k).

**The change** (`src/import.ts`): I build a `Map` from normalized email to position once, up front, then look each incoming contact up in it. New contacts are appended and registered in the map, so duplicates within the upload still merge with each other. Where the existing list already has two entries with the same email, the first one wins, as before. The function signature is unchanged, so `pipeline.ts` and `index.ts` need no edits.

**Test changes** (`test/import.test.ts`): I added one test that pins the "first existing entry wins" behavior, since the new lookup has to keep it.

**Verification:**
- `npm test`: 9 passed, 0 failed.
- `npx tsc --noEmit`: exit 0.
- Benchmark: 50k existing, 30k incoming, half overlapping with case and whitespace differences. Before: 73,914 ms. After: 51 ms. Both produced 65,000 rows.

I didn't touch `mergeContact` in `merge.ts`. It allocates a new tag `Set` per merge, but that is cheap next to the old scan and didn't show up in the timing.