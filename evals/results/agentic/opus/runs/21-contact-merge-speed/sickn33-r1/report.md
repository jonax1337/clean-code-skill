`mergeContacts` is now fast. A test that mimics your case, 30k incoming contacts into a book of 50k, takes about **0.13 s**. The old code took **about 73 s** on the same data.

**What was slow:** for every incoming contact, the old code searched the entire result list and re-normalized both emails at each step. That's roughly 2 billion string operations for an upload your size.

**The fix** is in `src/import.ts`. I normalize each existing email once and store it in a lookup table (a `Map`) that gives its position in the list. Each incoming contact then needs a single lookup, and newly added contacts go into the table so later duplicates in the same upload still find them. The results should be the same as before:
- Contacts are still added in the order they arrive, and they're still merged into the existing entry.
- If the address book already holds two entries with the same email, the incoming contact still merges into the first one, as before.
- A merge never changes an entry's email, so the lookup table stays accurate.

**Tests:** I added two tests to `test/import.test.ts`:
- one for the duplicate-entries case;
- one for the 50k + 30k size, which fails if a merge takes over 1 second.

All 10 tests pass and the type check is clean. My first draft of the size test expected the wrong contact count; the arithmetic error was mine, not a code bug, and I fixed it.

The 1-second limit leaves plenty of room, but a timing check like this could still fail now and then on a very slow CI machine. Tell me if you'd rather drop it or raise it.