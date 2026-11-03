`parseDuration` now returns milliseconds, and nothing in the code multiplies its result by 1000 any more.

**Changes**
- **`src/duration.ts`**: the unit table is now in milliseconds and the doc comment says so. I exported `MS_PER_SECOND` so callers that still need seconds don't each hard-code `1000`.
- **`cache.ts`, `retry.ts`, `scheduler.ts`**: removed the `* 1000`.
- **Three callers that need seconds, so a plain search-and-replace would have broken them:**
  - **`http.ts`**: `Retry-After` must be whole seconds, so it now divides by `MS_PER_SECOND`. The result is always whole because durations only come in whole seconds or larger.
  - **`report.ts`**: the text still shows seconds (`timeout 30s, ttl 300s`), using a small `inSeconds` helper.
  - **`validate.ts`**: the limits are now `MIN_TTL_MS = parseDuration("5s")` and `MAX_TTL_MS = parseDuration("1d")`, so they always match the "5s" and "1d" in the error messages.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

**Tests:** No test checked the three seconds-based callers, so I wrote tests for them first and ran them against the old code. They are `test/http.test.ts`, `test/report.test.ts`, and a below-minimum case plus an exact-limits case in `test/validate.test.ts`.
- Before the change: `npm test` 16 passed.
- After the change: `npm test` 16 passed, 0 failed, and `npm run typecheck` reports no errors.

**This breaks code outside this repo:** `parseDuration` is exported from `src/index.ts`, so any code outside this repo that calls it will now get values 1000× larger, with no compile error. It probably needs a major version bump or a changelog note.