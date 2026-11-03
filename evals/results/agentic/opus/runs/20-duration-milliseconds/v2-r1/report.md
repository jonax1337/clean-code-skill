`parseDuration` now returns milliseconds. I've updated everything that calls it, and all 12 tests and the type check pass.

**Callers that wanted milliseconds** now use the result directly, with the `* 1000` removed:
- `src/cache.ts` (TTL expiry)
- `src/retry.ts` (`backoffDelayMs`)
- `src/scheduler.ts` (`nextRun`)

**Callers that needed seconds** were the risky part. They would have silently become 1000× too large:
- `src/http.ts`: the `Retry-After` header must be in seconds, so it now divides by `MS_PER_SECOND`.
- `src/report.ts`: `describeSettings` prints values with an `s` suffix, so it divides too.
- `src/validate.ts`: the TTL limits are now in milliseconds, worked out from `"5s"` and `"1d"`. The error messages use those same strings, so the limit and its message can't drift apart.

**Other changes:**
- `src/duration.ts` exports a new `MS_PER_SECOND = 1000` constant, so the 1000 isn't repeated as a bare number.
- `test/duration.test.ts` now expects millisecond values.

`http.ts` and `report.ts` have no tests. I checked them by hand: `"2m"` gives `Retry-After: 120`, `describeSettings` prints `timeout 30s, ttl 3600s`, and `validateTtl` still rejects `"4s"` and accepts `"5s"`.

**This is a breaking change outside the repo:** `parseDuration` is part of the public API in `src/index.ts`, so any outside code that calls it will now get values 1000× larger. If anything outside this repo uses it, consider a major version bump; `package.json` is still at 1.0.0. I haven't committed anything.