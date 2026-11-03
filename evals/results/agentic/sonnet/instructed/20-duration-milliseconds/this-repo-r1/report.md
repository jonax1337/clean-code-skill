`parseDuration` now returns milliseconds, and the callers are updated. `npm test` passes (12 tests, 0 failures) and `tsc --noEmit` reports no errors.

- **`src/duration.ts`:** the unit table is now `MS_PER_UNIT`, and the doc comment says milliseconds.
- **`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`:** I removed the `* 1000`.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`. The error messages are unchanged (`5s`, `1d`).
- **`src/http.ts`, `src/report.ts`:** these still need seconds, so they now divide by 1000. `Retry-After` and the `describeSettings` text come out exactly as before, because durations are always whole seconds.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

I added no new tests, since existing ones already cover the changed callers except `http.ts` and `report.ts`. I did not find tests for those two, so their unchanged output is checked only by reasoning.