`parseDuration` now returns milliseconds, and I updated every caller to match. All 14 tests pass and `tsc --noEmit` shows no errors.

- **`duration.ts`:** the unit table is now in milliseconds, and the doc comment says so.
- **`cache.ts`, `retry.ts`, `scheduler.ts`:** I removed the `* 1000`.
- **`validate.ts`:** the TTL minimum and maximum are now in milliseconds. The error messages are unchanged.
- **`http.ts`:** `Retry-After` must stay in whole seconds, so it now divides by 1000 and rounds.
- **`report.ts`:** it still prints seconds, so it divides by 1000.
- **Tests:** I updated the expected values in `duration.test.ts`. I also added `test/units.test.ts`, with tests for `rateLimitHeaders` and `describeSettings`, which had none.

I haven't committed anything.