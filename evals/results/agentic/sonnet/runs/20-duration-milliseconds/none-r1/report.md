`parseDuration` now returns milliseconds, and the callers are updated to match. All 12 tests pass. I didn't run `npm run typecheck`.

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so.
- **Callers that wanted milliseconds** (`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`): I removed the `* 1000`.
- **Callers that wanted seconds** (`src/http.ts`, `src/report.ts`): I added `/ 1000`, so the `Retry-After` header and the "timeout …s, ttl …s" text come out exactly as before.
- **`src/validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`. The error messages are unchanged.
- **`test/duration.test.ts`**: the expected values are now in milliseconds. The other test files needed no changes.

I haven't committed anything.