`parseDuration` now returns milliseconds, and all 12 tests pass.

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so.
- **`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`**: removed the `* 1000`.
- **`src/http.ts`**: `Retry-After` has to be in whole seconds, so it now divides by 1000 and rounds.
- **`src/report.ts`**: the settings description still prints seconds, so it divides by 1000.
- **`src/validate.ts`**: the min and max TTL constants are now `MIN_TTL_MS` and `MAX_TTL_MS`, in milliseconds.
- **`test/duration.test.ts`**: updated the expected values to milliseconds.

I didn't add a test for the new rounding in `rateLimitHeaders`. Since the parser only accepts whole seconds or larger, the rounding never changes a result today.