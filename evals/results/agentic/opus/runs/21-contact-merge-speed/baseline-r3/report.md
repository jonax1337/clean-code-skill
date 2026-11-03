`mergeContacts` is fast now. On a synthetic test with 50k existing contacts and 30k incoming, it went from about **51 seconds to about 35 ms**, and the old and new versions gave identical results.

**Why it was slow:** for every incoming contact, `findIndex` searched the whole address book and recomputed `normalizeEmail` on both sides of each comparison. With your numbers that's over a billion string trims and lower-case conversions.

**What changed** (`src/import.ts`): it now builds a lookup table from normalized email to position in the list, once. Each incoming contact then needs one lookup instead of a full search. New contacts are added to the table as they're appended, so duplicates within the same upload still merge with each other.

**Behaviour is the same:**
- If the stored book already holds two contacts with the same email, incoming matches still merge into the first one, as before.
- New contacts are still added in the order they arrive.
- Matching still ignores case and surrounding whitespace.

All 8 tests and the typecheck pass. I haven't committed the change.