`parseDuration` now returns milliseconds and the callers are updated. All 16 tests pass and the typecheck is clean. It's committed on `main`, but the push failed because the repo has no git remote.

**The three callers that already wanted ms:** I removed the `* 1000` from `cache.ts`, `retry.ts` and `scheduler.ts`.

**Three callers used the result as seconds directly.** A plain search for `* 1000` wouldn't have found these, and they would have broken silently:
- `src/http.ts`: the `Retry-After` header has to be in seconds, so it now divides by 1000. Otherwise `"2m"` would have sent `120000` instead of `120`.
- `src/report.ts`: prints values with an `s` suffix, so it also divides by 1000.
- `src/validate.ts`: the TTL limits (5s minimum, 1 day maximum) are now in ms. Without this, every TTL from 6s to 1d would have been rejected for being over the maximum.

**Log:**
1. I found every caller and noticed that `http`, `report` and the `validate` minimum had no tests.
2. I added tests that lock in their current seconds-based behavior (`test/http.test.ts`, `test/report.test.ts`, two cases in `test/validate.test.ts`). All 16 passed. Commit `1c20565`.
3. I changed `test/duration.test.ts` to expect ms. It failed for the expected reason (`actual: 30, expected: 30000`).
4. I switched `src/duration.ts` to ms and updated the six callers. Tests (16/16) and `tsc --noEmit` pass. Commit `8e7c9a9`.
5. The push to `main` failed because no remote is configured. Add one and push when you're ready.

I didn't run the skill's crapper, dryer and mutator tools: the skill directory doesn't include them, and this change doesn't add any branching.

The `/ 1000` is always exact, because the parser only accepts whole seconds or larger units.