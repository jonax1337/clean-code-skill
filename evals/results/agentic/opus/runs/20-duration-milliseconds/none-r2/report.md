`parseDuration` now returns milliseconds, and the code that calls it has been updated to match. All 12 tests pass and `tsc --noEmit` shows no errors.

**Callers that wanted milliseconds:** I removed the `* 1000` in three places:
- `src/cache.ts:17` (cache expiry)
- `src/retry.ts:14` (retry backoff)
- `src/scheduler.ts:11` (next scheduled run)

**Callers that wanted seconds:** these used the old return value as-is, so they would have broken without a change:
- **`src/validate.ts`**: the TTL limits are now in ms (`MIN_TTL_MS = 5 * 1000`, `MAX_TTL_MS = 24h * 1000`). Without this, a `"5s"` TTL would have been read as 5000 seconds and every TTL over about 86 seconds would have been rejected as over the maximum.
- **`src/http.ts`**: `Retry-After` has to be whole seconds, so it now uses `Math.ceil(ms / 1000)`.
- **`src/report.ts`**: it divides by 1000 so the text still says e.g. `timeout 30s`.

**Tests:** I updated the expected values in `test/duration.test.ts` to milliseconds.

`parseDuration` is also exported publicly from `src/index.ts`, so this is a breaking change for any outside code that uses it. Any version bump or changelog note is up to you.