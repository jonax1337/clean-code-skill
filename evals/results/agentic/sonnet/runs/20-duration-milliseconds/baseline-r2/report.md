`parseDuration` now returns milliseconds, and all 12 tests pass.

- **`src/duration.ts`:** The unit table is now in milliseconds, and the doc comment says so.
- **Callers that multiplied by 1000:** I removed the `* 1000` in `cache.ts`, `scheduler.ts` and `retry.ts`.
- **Callers that wanted seconds:**
  - `http.ts` divides by 1000 and rounds down, because `Retry-After` is in whole seconds.
  - `report.ts` divides by 1000 for its "…s" output.
- **`src/validate.ts`:** The TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparison is in milliseconds.
- **`test/duration.test.ts`:** The expected values are now in milliseconds.

I didn't add a test for `rateLimitHeaders` or `describeSettings`, so the tests don't check the new division in `http.ts` or `report.ts`.