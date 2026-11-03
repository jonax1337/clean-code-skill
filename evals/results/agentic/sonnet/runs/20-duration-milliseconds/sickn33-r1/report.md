`parseDuration` now returns milliseconds, and the callers are adapted. All 12 tests pass. I didn't run `npm run typecheck`.

- **`src/duration.ts`**: the unit table is now `MILLISECONDS_PER_UNIT`, and the doc comment says milliseconds.
- **Callers that wanted milliseconds**: I dropped the `* 1000` in `src/cache.ts`, `src/retry.ts` and `src/scheduler.ts`.
- **Callers that wanted seconds**:
  - `src/http.ts` now divides by 1000 for the `Retry-After` header, which is specified in seconds.
  - `src/report.ts` divides by 1000 so the `…s` text it prints is unchanged.
- **`src/validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `milliseconds`. The error messages are unchanged.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

The tests I ran don't exercise `rateLimitHeaders` or `describeSettings`, so I checked those two only by reading the code.