Imports of 30k contacts into a 50k book now take about 0.1 s instead of about 90–106 s. The full test suite passes (9/9) and the typecheck is clean. I haven't committed anything, since you didn't ask for a commit.

**The cause:** for every incoming contact, `mergeContacts` ran a linear `findIndex` over the whole result, and it re-normalized every existing email on each pass. That is roughly 30k × 50k normalizations.

**The fix** (`src/import.ts`): build a `Map` from normalized email to index once, from the existing contacts. Each incoming contact is then a single lookup. New contacts are added to the map as they are appended, so duplicates within the same upload still merge. The behavior is unchanged: the first existing match wins, matching is case- and whitespace-insensitive, and arrival order is kept.

**The test** (`test/import.test.ts`): I added a regression test with 50k existing contacts and 30k incoming, 10k of them matching and 20k new. It asserts the result length and that the run finishes in under 1 s. On the old code it failed at 106 s. On the new code it takes about 112 ms.

**Log of actions:**
1. Read `src/import.ts`, its helpers (`merge.ts`, `normalize.ts`), `types.ts`, `package.json`, and the existing import tests.
2. Added the 30k/50k performance test and ran it. The first run failed because my fixture's expected count was wrong; I corrected it.
3. Reran the test on the unchanged code. It failed on the time assertion (106 s), confirming the bottleneck.
4. Replaced the `findIndex` loop with the `Map` index.
5. Ran `npm test` (9/9 pass) and `npm run typecheck` (clean).

The 1 s budget in the test is a machine-dependent threshold. The measured time has a wide margin, so it should not be flaky, but it is still a timing assertion. The skill's Crapper and Mutator tools were not available in this environment, so I did not run them.