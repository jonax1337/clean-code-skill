`mergeContacts` is now linear instead of quadratic. A 50k-contact book merged with a 30k-row upload takes about 29 ms here, where the old version took minutes. The change is in `src/import.ts`, and I haven't committed it.

**What was slow:** for each incoming row, `findIndex` scanned the whole result array and re-normalized every existing email. That is roughly 30k × 50k string operations per upload.

**The fix:** I build a `Map` from normalized email to position once, then each incoming row does a single lookup. Behavior is unchanged:
- Matching still uses `trim().toLowerCase()`.
- If the existing list has duplicate emails, the first one still wins, as with `findIndex`.
- Incoming duplicates still merge into one entry, and new contacts are still appended in arrival order.

**Verification:**
- `npm test`: all 8 tests pass.
- `npm run typecheck`: passes.
- The 29 ms figure comes from one synthetic benchmark I ran, not from your real CSV. I didn't time the old code on the same input, so the "minutes" comparison is from your report.

If the import is still slow after this, the cost is probably in CSV parsing or in the save step rather than the merge. I can profile the full `importCsv` path next if you want.