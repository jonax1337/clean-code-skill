`parseDuration` now returns milliseconds. All 12 tests pass and the typecheck is clean.

- **`src/duration.ts`:** the unit table is now `MS_PER_UNIT` (`s: 1000` up to `d: 86_400_000`), and the doc comment says milliseconds.
- **Callers that wanted milliseconds:** I dropped the `* 1000` in `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that need seconds:** `http.ts` (the `Retry-After` header) and `report.ts` (the `describeSettings` text) now divide by 1000. Their output is the same as before.
- **`validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`. The error messages are unchanged.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

`src/index.ts` re-exports `parseDuration`, so any outside code that imports it will now get milliseconds instead of seconds.