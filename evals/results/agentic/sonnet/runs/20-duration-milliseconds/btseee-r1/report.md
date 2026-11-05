`parseDuration` now returns milliseconds, and every caller is adapted. `npm test` passes (12 of 12). I didn't run `npm run typecheck`.

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so.
- **Callers that wanted ms**: I dropped the `* 1000` in `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that wanted seconds**: `http.ts` (`Retry-After`) and `report.ts` (the `…s` text) now divide by 1000. This keeps their output the same, since the inputs are whole seconds.
- **`validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local `seconds` variable is renamed `ms`.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.