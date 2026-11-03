`parseDuration` now returns milliseconds, and every caller has been updated. All 12 tests pass and `tsc --noEmit` reports no errors.

**Removed the `* 1000`** (these callers already wanted milliseconds):
- `src/cache.ts:17`: cache entry expiry
- `src/retry.ts:14`: retry backoff delay
- `src/scheduler.ts:11`: next job run time

**Added `/ 1000`** (these callers need seconds, and would otherwise be off by a factor of 1000 without failing):
- `src/http.ts:5`: the `Retry-After` header has to be in seconds.
- `src/report.ts:9`: the settings text prints the timeout and TTL with an `s` suffix.

**Also changed:**
- `src/validate.ts`: the min/max TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), so validation behaves the same as before.
- `test/duration.test.ts`: the expected values are now in milliseconds.

`parseDuration` is also exported from `src/index.ts`, so any outside code that calls it will now get values 1000× larger. Nothing in this repo is affected, but if other code uses this package, this is a breaking change and probably needs a major version bump.

I haven't committed anything.