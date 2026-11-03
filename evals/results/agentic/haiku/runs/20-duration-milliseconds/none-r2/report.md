`parseDuration` now returns milliseconds, and every caller is adjusted. All 12 tests pass and `npm run typecheck` runs clean.

Changes:
- **`src/duration.ts`**: multiplies by 1000 before returning; doc comment updated.
- **`src/cache.ts`**, **`src/retry.ts`**, **`src/scheduler.ts`**: dropped the `* 1000` they had been doing.
- **`src/validate.ts`**: the min/max TTL constants are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), so the comparison works without conversion. The error messages still say "5s" and "1d".
- **`src/http.ts`** and **`src/report.ts`**: divide by 1000 at the point of output, since `Retry-After` is in whole seconds and the report prints `s` values.
- **`test/duration.test.ts`**: expected values are now milliseconds.

Decision for you: `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for any external consumer of the package. If the package has users, you may want a changelog note or a major version bump. I did not make that call for you.

I haven't committed anything.