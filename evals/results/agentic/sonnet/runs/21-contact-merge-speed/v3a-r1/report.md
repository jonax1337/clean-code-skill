I rewrote `mergeContacts` in `src/import.ts` to look up emails in a `Map` instead of scanning the whole list for each incoming contact. The old version scanned the list and re-normalized every address on every lookup, which is why 30k incoming against 50k existing took minutes. It now normalizes each email once and does one lookup per incoming contact, so the work grows roughly linearly with the number of contacts.

I did not time it on a 30k × 50k input.

Behavior is the same as before:
- **Duplicates within the existing book:** a new contact merges into the first matching entry, as `findIndex` did.
- **Duplicates within the upload:** later copies merge into the first, because each appended contact is registered in the map.
- **Order:** new contacts are still appended in arrival order.

`npm test` passes (8 of 8) and `tsc --noEmit` is clean. I didn't add a test. The existing `import.test.ts` still runs, but I didn't check whether it covers the duplicate cases above.

I only read `import.ts`, `merge.ts`, `normalize.ts` and `types.ts`. If the import is still slow, the CSV parsing in `csv.ts` or `pipeline.ts` is the next place I'd look. I haven't checked either.