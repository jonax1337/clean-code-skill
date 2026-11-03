`parseDuration` now returns milliseconds, and every caller has been updated.

**Callers that wanted milliseconds:** I removed the `* 1000` from `cache.ts`, `retry.ts` and `scheduler.ts`.

**Callers that really wanted seconds:** these would have been wrong after the change:
- `http.ts`: the `Retry-After` header must be in whole seconds, so it now divides by `MS_PER_SECOND`. Durations only come in whole units, so the result is still a whole number.
- `report.ts`: the summary text still shows seconds (`timeout 30s, ttl 300s`).
- `validate.ts`: the TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), so the comparisons stay correct.

`MS_PER_SECOND` is a new export in `src/duration.ts`, so the 1000 is written in one place only. The function's name and signature haven't changed, but it's re-exported from `index.ts`. Any outside code that relies on it returning seconds will now get values 1000 times larger.

**Tests:** `http`, `report` and the TTL minimum had no tests, so I wrote tests for them first and checked they passed on the old code before changing anything:
- `test/http.test.ts`
- `test/report.test.ts`
- two new cases in `test/validate.test.ts`: below the minimum, and exactly at the minimum and maximum

I changed the expected values in `test/duration.test.ts` to milliseconds.

**Checks:**
- `npm test`: 16 tests, 16 passed, 0 failed, both before and after the change.
- `npm run typecheck` (`tsc --noEmit`): no errors.

Nothing is committed yet.