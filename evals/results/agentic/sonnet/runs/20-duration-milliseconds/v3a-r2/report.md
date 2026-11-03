`parseDuration` now returns milliseconds, and I updated every caller to match. `npm test` passes (12 of 12) and `npm run typecheck` reports no errors.

- **`src/duration.ts`:** the unit table is now `MS_PER_UNIT` (`s: 1000` through `d: 86_400_000`), and the doc comment says milliseconds.
- **`cache.ts`, `retry.ts`, `scheduler.ts`:** I removed the `* 1000`.
- **`validate.ts`:** the limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`. The error messages are unchanged.
- **`http.ts`:** `Retry-After` must be in seconds, so it now divides by 1000.
- **`report.ts`:** the description string still shows seconds, so it divides by 1000.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

All units are whole seconds or larger, so the divisions in `http.ts` and `report.ts` never produce fractions.

I didn't add new tests. I didn't check whether anything outside `src` and `test` calls `parseDuration`. It is exported from `src/index.ts`, so outside users of the package would see the unit change.