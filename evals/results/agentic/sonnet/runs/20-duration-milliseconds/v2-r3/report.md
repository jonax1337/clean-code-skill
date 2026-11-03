`parseDuration` now returns milliseconds, and the rest of the code is adapted to match. All 12 tests and the typecheck pass.

- **`src/duration.ts`**: the unit table is now in milliseconds (`s: 1000` up to `d: 86_400_000`), and the doc comment says so.
- **Callers that multiplied by 1000** (`cache.ts`, `retry.ts`, `scheduler.ts`): I removed the `* 1000`.
- **`validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ttlMs`. The error messages are unchanged.
- **Callers that need seconds**: `http.ts` divides by a new `MS_PER_SECOND` constant for `Retry-After`. `report.ts` divides by 1000 so its output still reads "…s".
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

I used a bare `/ 1000` in `report.ts` but a named constant in `http.ts`. Say if you'd like them to match.