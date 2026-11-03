`parseDuration` now returns milliseconds. I ran the tests and the typecheck afterwards: all 16 tests pass (12 before, 16 now) and `tsc --noEmit` is clean.

**Changed**
- **`src/duration.ts`:** the unit table holds milliseconds now (`MS_PER_UNIT`), and the doc comment says so.
- **Callers that only wanted milliseconds:** I removed `* 1000` from `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that need seconds:**
  - `http.ts`: the `Retry-After` header must be whole seconds, so it divides by 1000. Every unit is a whole number of seconds, so the result is always a whole number.
  - `report.ts`: still prints seconds (`timeout 30s, ttl 300s`), so it divides by 1000.
  - `validate.ts`: the min/max TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages are unchanged.

**Tests**
- I updated the expected values in `test/duration.test.ts`.
- I added tests for the callers that need seconds, which had no tests before and would have broken without any error: `test/http.test.ts`, `test/report.test.ts`, plus minimum and within-bounds cases in `test/validate.test.ts`.

**Breaking change:** `parseDuration` is exported publicly from `src/index.ts`, so any code outside this repo that calls it will now get values 1000× larger. All callers inside the repo are updated.

Nothing is committed yet.