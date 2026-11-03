`parseDuration` now returns milliseconds, and every caller is updated. All 14 tests pass (up from 12, with 2 new characterization tests) and `tsc --noEmit` is clean.

**What changed**

- `src/duration.ts`: returns milliseconds. The unit table is now in ms, and `MS_PER_SECOND` is exported so the seconds-based callers share one definition.
- `src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`: dropped the `* 1000`.
- `src/http.ts`: `Retry-After` still sends whole seconds, so it divides by `MS_PER_SECOND`.
- `src/report.ts`: the settings text still reads `timeout 30s, ttl 300s`, so it divides by `MS_PER_SECOND`.
- `src/validate.ts`: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`. The error messages are unchanged.
- Tests: `test/duration.test.ts` now expects ms. I also added `test/http.test.ts` and `test/report.test.ts` to pin the seconds output those two modules must keep.

**Choices I made**

- I kept the user-visible output in seconds (`Retry-After` and the report text) rather than switching it to ms, since the request was about the internal return value.
- I did not commit. You asked for the change, not a commit, so the work is uncommitted in the working tree.

**Things to know**

- `parseDuration` is exported from `src/index.ts`, so any external consumer that read seconds will now get ms. That is the intended change, but it is a breaking API change for the package.
- The ub-mode quality tools (crapper, dryer, mutator) are not available in this environment, so I skipped those steps.

**Log**

1. Read `src/duration.ts`, every caller, and the existing tests. Baseline: 12 passing, typecheck clean.
2. Updated `test/duration.test.ts` to ms expectations. Confirmed the two affected tests fail with `actual: 30, expected: 30000`.
3. Added characterization tests for `rateLimitHeaders` and `describeSettings`, which pass before and after the change.
4. Changed `duration.ts` to ms and updated the six callers. Re-ran tests: 14/14 pass, typecheck clean.