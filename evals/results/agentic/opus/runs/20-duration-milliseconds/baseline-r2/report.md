`parseDuration` now returns milliseconds, and the rest of the code is adapted. All 12 tests pass and `tsc --noEmit` reports no errors.

**Callers that wanted milliseconds:** I removed the `* 1000`.
- `src/cache.ts`: TTL expiry
- `src/retry.ts`: `backoffDelayMs`
- `src/scheduler.ts`: `nextRun`

**Callers that need seconds:** these now divide by 1000. Simply removing the multiplication wouldn't work here.
- `src/http.ts`: the `Retry-After` header must be in seconds.
- `src/report.ts`: the summary prints values with an `s` suffix.
- `src/validate.ts`: the min and max TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), so the checks behave exactly as before.

**Tests:** I updated the expected values in `test/duration.test.ts` to milliseconds.

`src/index.ts` exports `parseDuration` publicly, so any code outside this repo that calls it will now get values 1000× larger. If other projects use it, treat this as a breaking change, for example with a major version bump.