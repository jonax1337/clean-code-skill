`parseDuration` now returns milliseconds. All 16 tests pass and `tsc --noEmit` is clean.

**What changed**
- **`src/duration.ts`**: the unit table is now in milliseconds, and the function exports a `MS_PER_SECOND` constant.
- **Callers that wanted milliseconds** (`cache.ts`, `retry.ts`, `scheduler.ts`): I removed the `* 1000`.
- **Callers that actually wanted seconds**: three places use the value as seconds, and only one of them had any test coverage. Without a fix they would have silently been off by 1000×:
  - `http.ts`: the `Retry-After` header has to be in seconds by spec, so it now divides by `MS_PER_SECOND`.
  - `report.ts`: `describeSettings` prints values like `30s`, so it also divides by `MS_PER_SECOND`.
  - `validate.ts`: the TTL limits are now in milliseconds, defined as `parseDuration("5s")` and `parseDuration("1d")`. They can't drift from the "5s"/"1d" in the error messages.

**Tests**
- I updated the expected values in `test/duration.test.ts` to milliseconds.
- Before making the change, I added tests for the three seconds-based callers and confirmed they passed on the old code: `test/http.test.ts`, `test/report.test.ts`, and checks on the minimum and both limits in `test/validate.test.ts`. They still pass after the change, so behavior is the same.

**Note:** `parseDuration` is part of the public API (re-exported from `src/index.ts`). Any code outside this repo that calls it will now get milliseconds, so this is a breaking change for those users and needs a major version bump or a changelog entry.

Nothing is committed yet.