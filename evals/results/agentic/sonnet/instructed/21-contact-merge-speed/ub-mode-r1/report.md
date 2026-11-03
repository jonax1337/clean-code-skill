`mergeContacts` in `src/import.ts` now builds a lookup of email to position once, instead of scanning the whole address book for every incoming contact. The old code did that scan and re-normalized every email each time, about 1.5 billion operations for 30k contacts against 50k. Now it's one pass over each list.

Behavior is unchanged. When the address book already has duplicate emails, the first one still wins. Duplicates inside the upload still merge into the entry added earlier. The existing tests (8, including the four `mergeContacts` ones) pass and the typecheck is clean.

I didn't time it on a 30k/50k input, and I didn't add a new test, since the existing ones already cover the merge behavior. I also haven't committed anything.