`parseDuration` now returns milliseconds, and I updated every caller. `npm test` passes (12 of 12) and `tsc --noEmit` reports no errors.

- **`src/duration.ts`**: the unit table is now in milliseconds, and I export a `MS_PER_SECOND` constant. I updated the doc comment to match.
- **Callers that dropped their `* 1000`**: `cache.ts`, `retry.ts` and `scheduler.ts`.
- **`validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, built from `MS_PER_SECOND`. The error messages are unchanged.
- **Callers that needed seconds**: `http.ts` (the `Retry-After` header) and `report.ts` (the settings text) now divide by `MS_PER_SECOND`. Output is the same as before.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

I didn't find existing tests for `http.ts` or `report.ts`, and I didn't add any, so the seconds conversion in those two files is checked only by the type checker.