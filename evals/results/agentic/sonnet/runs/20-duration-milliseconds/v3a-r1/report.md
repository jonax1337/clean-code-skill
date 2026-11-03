`parseDuration` now returns milliseconds, and every caller is adapted. `npm test` passes (12 of 12) and `npm run typecheck` reports no errors.

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so.
- **`cache.ts`, `retry.ts`, `scheduler.ts`**: I removed the `* 1000`.
- **`http.ts`**: `Retry-After` must be in seconds, so it now divides by 1000. Durations are whole seconds, so the result is always a whole number.
- **`report.ts`**: the output still shows seconds, so it divides by 1000.
- **`validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ttlMs`.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

`parseDuration` is also exported from `src/index.ts`, so any external consumer of the package that expects seconds will break. That is a public API change.

I didn't add tests for `http.ts` or `report.ts`. None existed, so I checked those two conversions by reading the code, not by running them.