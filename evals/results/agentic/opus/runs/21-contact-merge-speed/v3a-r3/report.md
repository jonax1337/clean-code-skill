`mergeContacts` is fixed. On a synthetic import of 30k contacts into a 50k book, it went from **81.5 s to 24 ms**.

**Cause:** for every incoming contact, `findIndex` scanned the whole list and called `normalizeEmail` on both emails each time. That's about 2 billion string operations.

**Fix** (`src/import.ts`): the function now builds a map from normalized email to list position once, and each incoming contact is a single lookup. New contacts go into the map as they're added, so duplicates within the same upload still merge with each other.

**Behavior is unchanged, including one edge case:** if the existing book already contains two entries with the same email, the old code merged into the *first* one. The map keeps the first position too. I added a test for this in `test/import.test.ts`, since none of the existing tests covered it.

**Checks:**
- `npm test`: 9 passed, 0 failed
- `npm run typecheck`: no errors
- The benchmark was a throwaway script with made-up data (20k matching emails, 10k new ones), run once on the old code and once on the new. I deleted it afterwards.

I didn't touch any other part of the import (CSV parsing, `mergeContact`) or look at how long they take. If uploads still feel slow, the time is being spent outside `mergeContacts`.