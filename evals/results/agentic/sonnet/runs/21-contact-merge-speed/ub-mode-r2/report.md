`mergeContacts` is now fast: a 50k-contact book with a 30k-contact import takes about 65 ms, down from about 56 s. All 10 tests pass. The commit is on `main`, but the push didn't go through because no remote or upstream branch is configured.

**Cause:** for every incoming contact, it scanned the whole result with `findIndex`. That re-normalized every existing email each time, so the work grew with existing × incoming.

**Fix (`src/import.ts`):** it now builds one `Map` from normalized email to index and looks contacts up in it. New contacts are added to the map as they're appended, so duplicates inside the upload still merge with each other. If the existing book already has the same email twice, the first entry still takes the merge, as before.

**Tests (`test/import.test.ts`):**
- A 50k/30k timing test with a generous 2 s limit. It failed before the fix, at about 56 s.
- A test that pins the first-duplicate behaviour.

I did not run the crapper, dryer or mutator tools from the skill, and `npm run typecheck` printed no errors.

To push, add a remote and run `git push -u origin main`, or tell me which remote to use.