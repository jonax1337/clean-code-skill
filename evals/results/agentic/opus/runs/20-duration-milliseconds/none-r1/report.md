`parseDuration` now returns milliseconds. All 12 tests pass and `tsc --noEmit` is clean.

**Callers that wanted milliseconds:** I removed the `* 1000` from these.
- `src/cache.ts:17`: TTL expiry
- `src/retry.ts:14`: backoff delay
- `src/scheduler.ts:11`: `nextRun`

**Callers that need seconds:** dropping the `* 1000` wouldn't have been enough for these. Without changes they would have quietly produced values 1000× too large.
- `src/http.ts:5`: the `Retry-After` header has to be whole seconds, so it now divides by 1000. The parser only accepts whole numbers of s/m/h/d, so the result is always a whole number.
- `src/report.ts:9`: the summary text shows seconds (`timeout 30s`), so it divides by 1000 too.
- `src/validate.ts`: the min/max TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages haven't changed.

**Tests:** `test/duration.test.ts` now expects millisecond values.

There are no tests for `http.ts` or `report.ts`, so the typecheck and test run don't cover those two changes. Also, `parseDuration` is exported from `src/index.ts`, so any outside code that uses it will now get milliseconds instead of seconds.