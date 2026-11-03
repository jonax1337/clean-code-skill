`parseDuration` now returns milliseconds, and all its callers are adapted. All 12 tests pass and `tsc --noEmit` is clean. I haven't committed anything.

**Log**
- **Tests first:** I changed the expectations in `test/duration.test.ts` to milliseconds. They failed for the expected reason (30 vs 30000).
- **`src/duration.ts`:** The unit table is now in milliseconds, and the doc comment says so.
- **`cache.ts`, `retry.ts`, `scheduler.ts`:** I dropped the `* 1000`. The conversion now lives only in `parseDuration`.
- **`validate.ts`:** The min and max TTL constants are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), and the local variable is renamed to match.
- **`http.ts`:** `Retry-After` is specified in whole seconds, so it now divides by 1000.
- **`report.ts`:** It still prints seconds, so it divides by 1000 there too.

I didn't run the crapper, dryer or mutator tools from the skill, because this change was a unit conversion and didn't add or reshape any functions.