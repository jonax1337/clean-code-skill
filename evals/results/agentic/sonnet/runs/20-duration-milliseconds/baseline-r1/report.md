`parseDuration` now returns milliseconds, and all the code that used it is adapted. All 12 tests pass.

- **`src/duration.ts`**: the unit table is now in milliseconds (`MS_PER_UNIT`), and the doc comment says milliseconds.
- **`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`**: removed the `* 1000`.
- **`src/validate.ts`**: the min and max TTL constants are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), and the local variable is `ms`.
- **`src/http.ts`**: `Retry-After` has to be in whole seconds, so it now divides by 1000 and rounds down. Every duration `parseDuration` accepts is a whole number of seconds, so the rounding changes nothing today.
- **`src/report.ts`**: the output text still says seconds, so it now divides by 1000.
- **`test/duration.test.ts`**: updated the expected values to milliseconds.

I haven't committed anything.