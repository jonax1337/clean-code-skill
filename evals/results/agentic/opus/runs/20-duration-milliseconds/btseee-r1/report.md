`parseDuration` now returns milliseconds. I updated every caller, and all 16 tests and the typecheck pass.

**Callers that wanted milliseconds:** I removed the `* 1000` from `src/cache.ts:17`, `src/retry.ts:14` and `src/scheduler.ts:11`.

**Callers that need seconds:** these would have been off by 1000× if left unchanged.
- **`src/http.ts`:** the `Retry-After` header must be in whole seconds, so it now divides by 1000. The result is always a whole number because the smallest unit is `s`.
- **`src/report.ts`:** `describeSettings` prints `…s`, so it also divides by 1000.
- **`src/validate.ts`:** the TTL bounds are now `MIN_TTL_MS = 5_000` and `MAX_TTL_MS = 24 * 60 * 60 * 1000`.

**Tests:** I updated the expected values in `test/duration.test.ts`. The `Retry-After` header, `describeSettings` and the minimum-TTL check had no tests, so before changing anything I added tests that lock in their current output: `test/http.test.ts`, `test/report.test.ts`, and two cases in `test/validate.test.ts`. Those tests pass before and after the change, so the change doesn't alter them.

**This changes a public function:** `parseDuration` is exported from `src/index.ts`, so any code outside this repo that calls it will now get values 1000× larger. You may want a version bump or a release note.

Nothing is committed.