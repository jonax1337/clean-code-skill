`mergeContacts` is now linear instead of quadratic. On a synthetic run with 50k existing and 30k incoming contacts, the merge takes about 50 ms.

**The cause:** for every incoming contact, `findIndex` scanned the whole result array and normalized every entry's email on each comparison. With 30k incoming against 50k+ existing, that is roughly a billion string operations.

**The fix** (in `src/import.ts`): I build a `Map` from normalized email to position once, up front. Each incoming contact is then a single lookup, and new contacts are added to the map as they are appended. Matching semantics are unchanged: the first entry with a given email is the merge target, the same as before, and output order is preserved.

**Verification:**
- `npm test`: 8/8 pass, including the existing merge and duplicate-email tests.
- `npm run typecheck`: clean. It was also clean before my change.
- The timing run was a throwaway script, which I deleted afterwards. The rest of the import path was not profiled. If the full upload is still slow after this, the CSV parsing in `src/csv.ts` is the next place to look.

I did not commit the change.