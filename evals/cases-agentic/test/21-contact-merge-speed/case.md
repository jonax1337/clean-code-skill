# Speeding up the contact import merge (TypeScript)

Tests a performance change on a hot path: replacing the quadratic lookup in `mergeContacts` with an index must keep the exact old behavior (first match wins among duplicate entries, trimmed case-insensitive keys, duplicates inside the upload, arrival order, no mutation of the inputs).

## Prompt

Importing a big CSV (around 30k contacts into an address book of 50k) takes minutes, and the time all goes into `mergeContacts` in `src/import.ts`. This runs on every upload, so please make it fast.
