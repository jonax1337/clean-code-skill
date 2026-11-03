`mergeContacts` is now linear. On a 50k-contact book with a 30k upload, it dropped from about 85 s to about 45 ms in my benchmark.

**The cause:** for each incoming contact, the old code scanned the whole result array and normalized the email of every entry on every comparison. That is roughly 1.5 billion normalizations for your case.

**The fix** (`src/import.ts`): I build a `Map` from normalized email to position once, then each incoming contact is a single lookup. The behavior is the same:
- If the stored book already has duplicate emails, the first entry still wins, as `findIndex` did.
- Merging keeps the existing entry's email, so the map keys stay valid.
- Contacts added from the upload are registered, so later duplicates inside the same upload still merge into them.

**Verification:**
- `npm test`: 9 of 9 pass. I added one regression test for the case where the stored book already contains duplicate emails.
- `npm run typecheck`: exits 0.
- The benchmark ran the original file from git and the new file on the same synthetic input. Both produced 65,000 contacts. I did not compare their output field by field.

I did not commit anything. The benchmark script is in `%TEMP%\bench-merge`, outside the repo.

The CSV parsing and `pipeline.ts` were not part of the timing you described, so I left them alone. If the whole upload still feels slow end to end, that is the next place to measure.