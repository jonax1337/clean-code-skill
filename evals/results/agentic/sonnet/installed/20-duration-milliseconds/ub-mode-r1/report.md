`parseDuration` now returns milliseconds, and all 12 tests pass. I haven't committed anything.

- **`src/duration.ts`:** the unit table is now milliseconds, and the doc comment says so.
- **Callers that multiplied by 1000:** `cache.ts`, `retry.ts` and `scheduler.ts` no longer multiply.
- **Callers that need seconds:**
  - `http.ts` divides by 1000 and rounds, so `Retry-After` stays in whole seconds.
  - `report.ts` divides by 1000 for the "…s" text.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparison still means 5 seconds to 1 day.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

I didn't add tests for `rateLimitHeaders` or `describeSettings`, so the existing tests don't cover the seconds conversions in `http.ts` and `report.ts`. I checked those two by reading the diff only.