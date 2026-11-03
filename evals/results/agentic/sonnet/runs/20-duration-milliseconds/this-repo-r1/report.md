`parseDuration` now returns milliseconds, and every caller is adapted. `node --test` passes (12 tests). `tsc --noEmit` printed no errors, but I only saw the tail of its output.

- **`src/duration.ts`**: the unit table is now `MS_PER_UNIT` (`s: 1000`, `m: 60_000`, and so on), and the doc comment says milliseconds.
- **Removed `* 1000`**: `cache.ts` (expiry), `retry.ts` (backoff delay) and `scheduler.ts` (next run).
- **Added `/ 1000`**: `http.ts` for the `Retry-After` header, which the spec defines in whole seconds, and `report.ts` for its `…s` output. Both get whole seconds because durations are integer seconds at minimum.
- **`src/validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ttlMs`. The error messages are unchanged.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

I didn't see tests covering `rateLimitHeaders` or `describeSettings`, so I haven't run the new `/ 1000` conversions in those two.