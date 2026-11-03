`parseDuration` now returns milliseconds, and the callers that did the `* 1000` conversion now use the result directly. All 12 tests pass and `tsc --noEmit` reports no errors.

Changes:

- **`src/duration.ts`**: multiplies by 1000 before returning, and the doc comment says milliseconds.
- **`src/cache.ts`**: `expiresAt` is `now + parseDuration(ttl)`.
- **`src/scheduler.ts`**: `nextRun` is `lastRun + parseDuration(every)`.
- **`src/retry.ts`**: `backoffDelayMs` is `parseDuration(base) * 2 ** attempt`.
- **`src/validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the comparison is in milliseconds. The error messages still read "5s" and "1d".
- **`src/http.ts`** and **`src/report.ts`**: these need seconds, so they divide by 1000. `Retry-After` and the `describeSettings` output are unchanged.
- **`test/duration.test.ts`**: the expected values are now milliseconds.

Things to know:

- `parseDuration` is re-exported from `src/index.ts`, so anyone importing it from the package gets milliseconds now. That is a breaking change for external callers, and it should go in the changelog or version bump if this is published.
- The `/ 1000` in `http.ts` and `report.ts` is a literal, as the original code had. I didn't add an exported constant for it.
- I did not commit anything.