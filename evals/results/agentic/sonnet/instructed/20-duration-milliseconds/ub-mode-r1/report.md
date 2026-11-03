`parseDuration` now returns milliseconds, and the rest of the code is adapted. All 12 tests pass. I didn't run a type-check or any of the ub-mode tools (crapper, dryer, mutator), and I didn't commit.

- **`src/duration.ts`:** the unit table is now in milliseconds (`s: 1000`, `m: 60_000`, and so on), and the doc comment says milliseconds.
- **Callers that wanted milliseconds:** I dropped the `* 1000` in `src/cache.ts`, `src/retry.ts` and `src/scheduler.ts`.
- **Callers that wanted seconds:** `src/http.ts` (the `Retry-After` header) and `src/report.ts` (the settings description) now divide by 1000, so their output is unchanged.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparisons stay in milliseconds. The error messages are unchanged.
- **`test/duration.test.ts`:** I updated the expected values to milliseconds.

I changed the duration tests and ran the whole suite once after the source edits. I didn't first run the updated tests against the old code to watch them fail.

I added no new tests for `src/http.ts` and `src/report.ts`. The existing suite doesn't appear to cover them, so their `/ 1000` conversions have no test.