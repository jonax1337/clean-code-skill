`parseDuration` now returns milliseconds, and the other code is adapted to that. The 12 tests pass; I didn't run `npm run typecheck`.

- **`src/duration.ts`:** the unit table is now in milliseconds and the doc comment says so.
- **Callers that multiplied by 1000:** I dropped the `* 1000` in `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that need seconds:** `http.ts` (the `Retry-After` header) and `report.ts` (the `…s` display text) now divide by 1000, so their output is unchanged.
- **`src/validate.ts`:** the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, compared against milliseconds.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.