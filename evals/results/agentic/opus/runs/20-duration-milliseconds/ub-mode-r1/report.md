`parseDuration` now returns milliseconds. All 14 tests pass and the typecheck is clean.

**What changed**
- **`src/duration.ts`:** the unit table is now in milliseconds and the doc comment says so.
- **`cache.ts`, `retry.ts`, `scheduler.ts`:** these wanted milliseconds, so I removed their `* 1000`.
- **Places that still need seconds:**
  - **`http.ts`:** the `Retry-After` header is defined in seconds, so it divides by 1000.
  - **`report.ts`:** the settings text prints "…s", so it also divides by 1000.
  - **`validate.ts`:** it now compares against limits in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages are the same.

Durations are always whole units, so `/ 1000` always gives a whole number of seconds.

**Log**
1. Found every caller. Three of them (`http`, `report`, `validate`) used the result as seconds, so they needed converting rather than just dropping `* 1000`.
2. `http` and `report` had no tests, so I added `test/http.test.ts` and `test/report.test.ts` to lock in their current output. Both passed before the change.
3. Changed `test/duration.test.ts` to expect milliseconds. It failed as expected (got 30, expected 30000).
4. Changed `parseDuration` and its callers. All 14 tests pass, including the existing cache, retry and scheduler tests, which exercise the millisecond paths.
5. Made two commits: `36e311f` adds the tests, `91912da` makes the change.

**Not done**
- **Push:** the repo has no remote, so the commits are only on local `main`.
- **Crapper, dryer and mutator checks:** the skill calls for these tools, but none are in the repo or the skill folder, so I didn't run them.

`parseDuration` is part of the public exports in `index.ts`, so anyone outside this repo who calls it will now get milliseconds instead of seconds. That's a breaking change for them and probably needs a major version bump.