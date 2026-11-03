`mergeContacts` now runs in about 50 ms for a 50k-contact book merged with a 30k-contact upload, down from minutes. The change is in `src/import.ts`.

The old loop called `findIndex` for every incoming contact, scanning the whole result array and re-normalizing every stored email each time. The new version builds a `Map` from normalized email to row index once, up front, then does an O(1) lookup per incoming contact. Each email is normalized once per lookup instead of once per comparison.

Two behaviors are kept from the old code:
- If the existing book already has duplicate emails, the first row still wins. The map only records the first occurrence.
- A merged row keeps its original position and email. New rows are appended in arrival order, and duplicates within the upload merge into the row they created.

Verification:
- `npm test`: all 8 tests pass.
- `npm run typecheck`: clean.
- I compared the old and new implementations on 500 random inputs with duplicates, whitespace and mixed case. The outputs matched exactly. That check was a throwaway script outside the repo.

I didn't commit anything.