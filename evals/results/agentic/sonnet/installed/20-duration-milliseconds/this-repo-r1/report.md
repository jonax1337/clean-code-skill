`parseDuration` now returns milliseconds, and the code that called it is adapted. `npm test` gives 14 passed, 0 failed. `npm run typecheck` printed no errors.

- **`src/duration.ts`:** the unit table is now in milliseconds, and the doc comment says so.
- **Callers that wanted milliseconds:** `cache.ts`, `scheduler.ts` and `retry.ts` no longer multiply by 1000.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ttlMs`. The error messages are unchanged.
- **Callers that need seconds:** `http.ts` (the `Retry-After` header, which is specified in whole seconds) and `report.ts` (the "…s" text) now divide by 1000. Every unit is a whole number of seconds, so the result is always an integer.
- **Tests:** I updated the expected values in `test/duration.test.ts`. I also added `test/seconds-output.test.ts`, because nothing covered the `Retry-After` header or the settings description, and those are the two places where a unit mix-up would show.