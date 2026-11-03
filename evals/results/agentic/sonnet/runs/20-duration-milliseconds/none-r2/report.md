`parseDuration` now returns milliseconds, and every caller is adapted. All 12 tests pass.

- **`src/duration.ts`**: the unit table is now milliseconds (`MS_PER_UNIT`), and the doc comment says so.
- **Callers that want milliseconds**: I dropped the `* 1000` in `cache.ts`, `retry.ts` and `scheduler.ts`.
- **`src/http.ts`**: `Retry-After` has to be in whole seconds, so it now uses `Math.round(parseDuration(wait) / 1000)`.
- **`src/report.ts`**: the output still prints seconds, so it divides by 1000.
- **`src/validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

I didn't change or add any tests for `http.ts` or `report.ts`. The existing tests pass, but I haven't checked whether any of them exercise those two paths.