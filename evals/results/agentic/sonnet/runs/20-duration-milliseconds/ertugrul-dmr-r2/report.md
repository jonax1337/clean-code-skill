`parseDuration` now returns milliseconds, and all 12 tests pass.

- **`src/duration.ts`**: The unit table is now in milliseconds, built on a new exported `MILLISECONDS_PER_SECOND` constant (G25). The doc comment says milliseconds.
- **Callers that wanted milliseconds** (`cache.ts`, `retry.ts`, `scheduler.ts`): I removed the `* 1000`.
- **Callers that wanted seconds** (`http.ts`, `report.ts`): They now divide by `MILLISECONDS_PER_SECOND`. The `Retry-After` header and the settings description still come out in seconds.
- **`src/validate.ts`**: The TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `milliseconds`. The error messages are unchanged.
- **`test/duration.test.ts`**: The expected values are now in milliseconds.

I only ran the existing tests. No test covers `http.ts` or `report.ts`, so the seconds conversion in those two files isn't checked.