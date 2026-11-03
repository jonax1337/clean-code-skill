`parseDuration` now returns milliseconds, and every caller is adapted. `npm test` passes (12 passed, 0 failed) and `npm run typecheck` reports no errors.

- **`src/duration.ts`:** the unit table is now `MS_PER_UNIT` (`s: 1000`, `m: 60_000`, and so on), and the doc comment says milliseconds.
- **Callers that multiplied by 1000:** `cache.ts`, `retry.ts` and `scheduler.ts` no longer do. `retry.ts` still multiplies by `2 ** attempt`.
- **Callers that want seconds:** `http.ts` divides by 1000 for the `Retry-After` header, which the spec defines in whole seconds. `report.ts` divides by 1000 for its `…s` output.
- **`src/validate.ts`:** the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparisons stay in one unit. The error messages are unchanged.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

The divisions in `http.ts` and `report.ts` use a bare `/ 1000`. Both files have a single use, so I didn't add a shared constant.