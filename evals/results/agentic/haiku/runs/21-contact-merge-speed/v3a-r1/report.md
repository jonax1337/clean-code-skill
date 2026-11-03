`mergeContacts` is now fast. On a 30k-into-50k import it dropped from 69.5 s to 33 ms, and the output is identical to the old version.

**The cause:** for each incoming contact, `findIndex` scanned the whole result array and re-normalized every existing email on each comparison. That is O(n·m) work with repeated string normalization.

**The fix** (`src/import.ts`): build a `Map` from normalized email to index once, then look up each incoming contact in it. The function's behavior is unchanged:
- If the existing list already has duplicate emails, incoming contacts still merge into the first match, as before.
- Newly appended contacts are added to the map, so duplicates inside the upload still merge with each other.

**Verification:**
- `node --test`: 8/8 pass, same as before the change.
- `tsc --noEmit`: clean.
- Benchmark: I compared the old implementation (from `HEAD`) with the new one in a scratch directory on synthetic data with mixed-case and whitespace emails. Both produced the same JSON output. I deleted the scratch directory afterwards.

I didn't change `parseContactsCsv` or `toContactsCsv`, and I didn't profile them. If the end-to-end import is still slow after this, parsing or serialization is the next place to look. I also haven't added a regression test for the new code path, since the existing tests already cover its behavior. I haven't committed anything.