`parseDuration` now returns milliseconds, and the code that called it is adapted. `npm test` passes (12 of 12) and `npm run typecheck` is clean.

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so. I added an exported `MS_PER_SECOND` constant for callers that need seconds.
- **`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`**: removed the `* 1000`.
- **`src/http.ts`**: `Retry-After` is still whole seconds, now computed as `parseDuration(wait) / MS_PER_SECOND`.
- **`src/report.ts`**: the `timeout` and `ttl` values are divided by `MS_PER_SECOND`, so the output text is unchanged.
- **`src/validate.ts`**: the min and max TTL constants are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), and the local variable is renamed to `ms`.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

Because `parseDuration` is exported from `src/index.ts`, any outside consumer that expects seconds will silently get values 1000 times too large.

I didn't add tests for the callers that divide by `MS_PER_SECOND` (`http.ts`, `report.ts`) or for `validate.ts`. I didn't check whether any exist.