Merging 30k contacts into 50k now takes well under a second; before the fix it took about 82 seconds. All 10 tests pass, the typecheck is clean, and the change is committed locally as `a1743f4`. I haven't pushed it.

**Why it was slow:** for every incoming contact, `mergeContacts` scanned the whole growing list with `findIndex` and lowercased and trimmed every stored email again each time. That is about 30k × 50k, or roughly 1.5 billion comparisons.

**The fix** (`src/import.ts`): it now builds a lookup from normalized email to position once, then each incoming contact is a single lookup. The results are the same as before:
- New contacts are still appended in the order they arrive.
- New contacts are added to the lookup as they're appended, so duplicates within one upload still merge with each other.
- If the stored address book already has the same email twice, the first entry still gets the merge, as it did before.

**Log:**
1. Read `import.ts`, `merge.ts`, `normalize.ts` and the existing tests to see what `mergeContacts` must keep doing.
2. Added a test that pins the "first duplicate gets the merge" behaviour, since a careless lookup would change it.
3. Added a test that merges 30k into 50k and must finish within 1 second. It failed before the fix, at 81.8 seconds.
4. Replaced the scan with the lookup. All tests and the typecheck pass.
5. Committed with the reason, the change and the proof in the message.

**Two things to know:**
- The 1-second test is about timing. It has plenty of headroom here, but a very slow CI machine could make it flaky. You can loosen or drop it if that happens.
- The skill asks for crapper, dryer and mutator checks, but none of those tools are in this repo or environment, so I skipped them. The changed function is small and the tests cover each path through it.