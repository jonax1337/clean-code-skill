I rewrote `mergeContacts` in `src/import.ts` to use a hash lookup instead of a linear scan. I haven't run it or any tests.

The old code called `findIndex` for every incoming contact and normalized both emails on each comparison. That is about 30k × 50k comparisons, each with two string operations. The new code builds a `Map` from normalized email to index once, then does a constant-time lookup per incoming contact. The cost is now roughly proportional to 80k operations.

Results should be the same as before:
- **Duplicates already in `existing`:** the first occurrence wins, as `findIndex` did.
- **Repeated emails within the upload:** a contact added from the upload is registered in the map. A later duplicate in the same CSV merges into it, as it did before.
- **Order and merging:** output order and `mergeContact` behavior are unchanged. `mergeContact` keeps the existing email, so the map keys stay valid after a merge.