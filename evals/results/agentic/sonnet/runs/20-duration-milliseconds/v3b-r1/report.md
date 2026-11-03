`parseDuration` now returns milliseconds, and every caller is adapted. `npm test` passes (12 of 12) and `npm run typecheck` shows no errors.

- **`src/duration.ts`:** the unit table is now `MS_PER_UNIT`, and the doc comment says milliseconds.
- **Callers that wanted milliseconds:** I removed the `* 1000` in `cache.ts`, `retry.ts` and `scheduler.ts`.
- **Callers that wanted seconds:** `http.ts` (the `Retry-After` header) and `report.ts` (the settings description) now divide by a local `MS_PER_SECOND` constant. Their output is unchanged.
- **`src/validate.ts`:** the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ttlMs`. The error messages are the same.
- **`test/duration.test.ts`:** the expected values are now in milliseconds.

`parseDuration` is also re-exported from `src/index.ts`. Anyone outside this repo who imports it will now get milliseconds instead of seconds.

I didn't add a shared constant for `MS_PER_SECOND`. It's defined separately in `http.ts` and `report.ts`.