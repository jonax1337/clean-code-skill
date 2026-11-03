I rewrote `mergeContacts` in `src/import.ts` to look contacts up in a map instead of scanning the list. I haven't run it or any tests.

The old code called `findIndex` over the whole result for every incoming contact, normalizing the email on both sides each time. That is roughly 30k × 50k comparisons. The new code normalizes each email once and does one map lookup per incoming contact, so the cost grows with the number of contacts rather than with their product.

Behavior should be unchanged:
- **Duplicates in the existing book:** the first entry wins, as `findIndex` did.
- **Repeats within the upload:** a contact that repeats an email from earlier in the same upload is merged into the entry added earlier.
- **Order and merging:** output order and the merge logic are the same. The index map stays valid because `mergeContact` doesn't change the email.