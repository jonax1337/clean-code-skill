`parseDuration` now returns milliseconds, and all 12 tests pass.

- **`src/duration.ts`:** the unit table is now in milliseconds (`MS_PER_UNIT`), and the doc comment says milliseconds.
- **`cache.ts`, `retry.ts`, `scheduler.ts`:** I removed the `* 1000`.
- **`validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, in milliseconds. The error messages are unchanged.
- **`http.ts`:** `Retry-After` has to be in whole seconds, so it now divides by 1000 and rounds down.
- **`report.ts`:** `describeSettings` divides by 1000, so it still prints seconds.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

I didn't add tests for the `http.ts` and `report.ts` conversions.