`mergeContacts` is fast now. I ran a test with 50k existing contacts and 30k incoming ones, where half the incoming emails were already in the book. It dropped from about **64 s to about 40 ms**.

**Why it was slow:** for every incoming contact, `result.findIndex(...)` checked the whole list and cleaned up both email addresses on every comparison before matching them. That's about 30k × 65k comparisons, roughly 2 billion.

**The fix** (`src/import.ts`): it now builds a lookup table once, mapping each cleaned-up email to its position in the list. Each incoming contact is then found with a single lookup, so the work grows in step with the number of contacts instead of their product.

The results are the same as before, including the edge cases:
- **Duplicates in the upload:** a new contact goes into the table as soon as it's added, so later contacts in the same upload with the same email are merged into it.
- **Duplicates already in the book:** if two existing contacts share an email, only the first one goes into the table. That's the entry `findIndex` used to merge into, too.
- **Order:** the result keeps the same order, and new contacts are still added at the end in the order they arrive.

All 8 tests pass and the typecheck is clean. I haven't committed anything.