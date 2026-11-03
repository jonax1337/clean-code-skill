`parseDuration` now returns milliseconds, and the callers are adapted. `npm test` passes (12 of 12), but no test exercises `rateLimitHeaders` (`src/http.ts`) or `describeSettings` (`src/report.ts`), so those two changes are untested.

- **`src/duration.ts`:** the unit table is now in milliseconds, and I exported a `MILLISECONDS_PER_SECOND` constant (G25). The doc comment now says milliseconds.
- **Callers that wanted milliseconds:** `cache.ts`, `retry.ts` and `scheduler.ts` no longer multiply by 1000.
- **Callers that want seconds:** `http.ts` (the `Retry-After` header) and `report.ts` (the settings description) now divide by `MILLISECONDS_PER_SECOND`, so their output is unchanged.
- **`src/validate.ts`:** the TTL limits and the local variable are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages are unchanged.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.