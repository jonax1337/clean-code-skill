`mergeContacts` now handles a 30k-into-50k import in about 100 ms, down from about 80 seconds in the same test. All 10 tests pass and `tsc --noEmit` is clean. The changes are not committed.

**Cause:** for every incoming contact, the code scanned the whole result list and re-normalized every stored email on each comparison. That is roughly 1.5 billion normalize calls at your sizes.

**Fix (`src/import.ts`):** the stored emails are indexed once in a `Map` from normalized email to position. Each incoming contact is then a single lookup, and newly appended contacts are added to the index as they arrive. If the stored list already contains a duplicate email, the index keeps the first position, so the merge target is the same as before.

**Tests (`test/import.test.ts`, TDD):**
- Added a scale test that merges 30k contacts into 50k and asserts under 1 second. It failed at 80 s before the fix.
- Added a test pinning that an incoming contact merges into the first stored entry with a matching email. This guards the behavior the index must preserve.

**Not done:**
- I did not commit or push. You didn't ask for a commit, so I left the diff in the working tree. Say the word and I'll commit it in small steps.
- The ub-mode skill calls for the crapper, dryer, and mutator tools. I didn't run them. They aren't in this repo, and the change is only a few lines.
- I ran `npm install` to run the tests and deleted the `package-lock.json` it created, so the diff stays limited to the fix.