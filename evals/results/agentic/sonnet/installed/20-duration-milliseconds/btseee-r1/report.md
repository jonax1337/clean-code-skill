`parseDuration` now returns milliseconds, and every caller is adjusted. All 12 tests pass.

- **`src/duration.ts`:** the unit table is now in milliseconds (renamed to `MS_PER_UNIT`), and the doc comment says milliseconds.
- **Callers that dropped their `* 1000`:** `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that now divide by 1000:** `http.ts` for `Retry-After`, which is specified in whole seconds, and `report.ts` for the "…s" output.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

A fractional-second result can't happen, because the parser only accepts whole numbers of seconds or larger. So the `/ 1000` in `http.ts` and `report.ts` always yields an integer.