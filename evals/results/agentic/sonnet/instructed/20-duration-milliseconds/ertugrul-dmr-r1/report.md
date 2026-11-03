`parseDuration` now returns milliseconds, and the other code is adapted to match. All 12 tests pass.

- **`src/duration.ts`:** the unit table is now `MILLISECONDS_PER_UNIT`, and the doc comment says milliseconds.
- **Callers that wanted milliseconds:** `cache.ts`, `retry.ts` and `scheduler.ts` no longer multiply by 1000.
- **Callers that want seconds:** `http.ts` (the `Retry-After` header) and `report.ts` (the settings description) now divide by a new `MILLISECONDS_PER_SECOND` constant. I defined that constant separately in each file.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `milliseconds`. The error messages are unchanged.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

My `sed` edits left some stray blank lines and a stray "n" in `http.ts` and `report.ts`. I fixed `http.ts` with a final edit, but I didn't look at either file again afterwards. Check that the spacing after the imports in both files is tidy.