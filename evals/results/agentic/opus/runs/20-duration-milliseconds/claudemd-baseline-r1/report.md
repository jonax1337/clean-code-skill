`parseDuration` now returns milliseconds, and all six places that call it have been updated. All 15 tests pass and the typecheck is clean.

**Callers that wanted milliseconds:** I removed their `* 1000`:
- `src/cache.ts` (TTL expiry)
- `src/retry.ts` (`backoffDelayMs`)
- `src/scheduler.ts` (`nextRun`)

**Callers that wanted seconds:** a plain search for `* 1000` would have missed these, and they would have broken quietly. Each now converts back to seconds:
- `src/http.ts`: the `Retry-After` header has to be in whole seconds. It now uses `Math.ceil(ms / 1000)`.
- `src/report.ts`: `describeSettings` prints values like `30s`. It now divides by 1000.
- `src/validate.ts`: the TTL limits were in seconds (5s minimum, 1d maximum). I changed them to `MIN_TTL_MS` / `MAX_TTL_MS`.

**Tests:**
- Updated the expected values in `test/duration.test.ts` to milliseconds.
- Added `test/http.test.ts`, which checks `Retry-After` stays in seconds.
- Added `test/report.test.ts`, which checks the settings text.
- Added a test in `test/validate.test.ts` for the TTL limits (4s fails, 5s passes, 1d passes). Before, only the "too long" case was tested.

**This breaks the public API:** `parseDuration` is exported from `src/index.ts`, so any outside code that relies on it returning seconds will now get values 1000× too large. You may want a major version bump or a changelog entry. I haven't committed anything.