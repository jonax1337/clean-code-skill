`parseDuration` now returns milliseconds, and all 12 tests pass.

- **`src/duration.ts`:** The unit table is now `MILLISECONDS_PER_UNIT` and the doc comment says milliseconds.
- **Callers that wanted milliseconds:** I removed the `* 1000` in `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that wanted seconds:** `http.ts` (the `Retry-After` header) and `report.ts` (the settings description) now divide by 1000. Their output is unchanged.
- **`src/validate.ts`:** The TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `milliseconds`.
- **`test/duration.test.ts`:** The expected values are now in milliseconds.

I haven't committed anything.