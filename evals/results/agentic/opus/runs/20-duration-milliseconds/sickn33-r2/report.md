`parseDuration` now returns milliseconds, and every caller has been updated. All 12 tests pass and the typecheck is clean.

**Callers that wanted milliseconds** no longer multiply by 1000:
- `src/cache.ts` (cache expiry)
- `src/retry.ts` (`backoffDelayMs`)
- `src/scheduler.ts` (`nextRun`)

**Callers that need seconds** now divide by 1000, so what they produce is unchanged:
- `src/http.ts`: the `Retry-After` header must be in whole seconds. Every duration format is a whole number of seconds, so dividing always gives a whole number.
- `src/report.ts`: the text still shows `…s`. I added a small `durationInSeconds` helper so the division isn't written twice.

**`src/validate.ts`** compares against limits that are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages ("5s", "1d") are the same.

**Tests:** I updated the expected values in `test/duration.test.ts` to milliseconds.

Two things to be aware of:
- `src/index.ts` exports `parseDuration` publicly. If anything outside this repo uses it, it will now get values 1000× larger, so treat this as a breaking change.
- `http.ts` and `report.ts` have no tests. The two places that still convert to seconds were checked by reading the code, not by tests.