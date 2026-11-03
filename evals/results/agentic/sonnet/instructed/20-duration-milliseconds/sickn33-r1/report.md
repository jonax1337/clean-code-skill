`parseDuration` now returns milliseconds, and all 12 tests pass.

- **`src/duration.ts`**: the unit table and doc comment are now in milliseconds.
- **`src/cache.ts`, `src/scheduler.ts`, `src/retry.ts`**: removed the `* 1000`, since the value is already in milliseconds.
- **`src/validate.ts`**: the TTL min and max constants are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`).
- **`src/http.ts`**: `Retry-After` is still whole seconds, now computed as `Math.ceil(ms / 1000)`.
- **`src/report.ts`**: the output still shows seconds, so the value is divided by 1000 before formatting.
- **`test/duration.test.ts`**: expected values updated to milliseconds.

I added the `Math.ceil` in `src/http.ts` because the header must be an integer. Every parsed duration is a whole number of seconds, so it never changes the result.