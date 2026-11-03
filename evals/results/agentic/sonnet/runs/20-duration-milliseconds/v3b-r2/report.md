`parseDuration` now returns milliseconds, and every caller is adapted. `npm test` passes (12 of 12) and `npm run typecheck` is clean.

- **`src/duration.ts`**: The unit table is now in milliseconds and the doc comment says so. I added an exported `MS_PER_SECOND` constant.
- **`cache.ts`, `retry.ts`, `scheduler.ts`**: I removed the `* 1000`.
- **`http.ts`**: `Retry-After` is still in seconds, so the result is divided by `MS_PER_SECOND`.
- **`report.ts`**: The settings text still prints seconds, so it also divides by `MS_PER_SECOND`.
- **`validate.ts`**: The TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, built from `MS_PER_SECOND`.
- **`test/duration.test.ts`**: The expected values are now milliseconds.

The `Retry-After` and settings-text outputs have no tests. I confirmed they keep their old seconds output only by reading the code.

Git warns that CRLF line endings in the touched `src` files will be converted to LF the next time it touches them. I didn't change any line endings myself.