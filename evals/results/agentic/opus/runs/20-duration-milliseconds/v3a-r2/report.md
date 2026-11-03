`parseDuration` now returns milliseconds, and every caller has been updated to match.

**Callers that already wanted milliseconds:** `cache.ts`, `retry.ts` and `scheduler.ts` no longer multiply by 1000.

**Callers that still need seconds:**
- `http.ts`: the `Retry-After` header must be in whole seconds, so it divides by 1000. Durations only accept whole numbers of a unit, so the result is still a whole number.
- `report.ts`: the settings description still shows seconds (`timeout 30s`), so it also divides by 1000.
- `validate.ts`: the limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`) and it compares against those directly. The error messages are unchanged.

**Tests:** I changed the expected values in `test/duration.test.ts` to milliseconds.

**Checks:** `npm test` passes all 12 tests, both before and after the change. `tsc --noEmit` is clean.

**Caution:** `parseDuration` is exported publicly from `src/index.ts`. Any code outside this repo that calls it will now get values 1000× larger. If anyone else uses this package, it's a breaking change. You'd need a major version bump, or a new name like `parseDurationMs` to make the change visible.

None of the tests check `rateLimitHeaders` or `describeSettings`, the two functions that turn milliseconds back into seconds. I checked their conversion by reading the code, not by running a test.