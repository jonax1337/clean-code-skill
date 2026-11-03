`parseDuration` now returns milliseconds, and the call sites are adapted to match. `npm test` passes (12/12) and `tsc --noEmit` reports no errors.

Changes:
- **`src/duration.ts`**: returns ms. The unit table is now in ms, built from a new exported `MS_PER_SECOND = 1000` constant.
- **`src/cache.ts`**: `now + parseDuration(ttl)`, with the `* 1000` removed.
- **`src/retry.ts`**: `parseDuration(base) * 2 ** attempt`, with the `* 1000` removed.
- **`src/scheduler.ts`**: `job.lastRun + parseDuration(job.every)`, with the `* 1000` removed.
- **`src/validate.ts`**: the min/max bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`. The error messages are unchanged.
- **`src/http.ts`**: `Retry-After` is still whole seconds, so it divides by `MS_PER_SECOND`.
- **`src/report.ts`**: the output still reads in seconds, so it divides by `MS_PER_SECOND`. For example, `timeout 30s`.
- **`test/duration.test.ts`**: expected values are now ms.

Things to check:
- `parseDuration` is re-exported from `src/index.ts`, so any external caller that expected seconds will now get ms. That is a breaking change for the package's public API.
- I chose `MS_PER_SECOND` as a new export from `duration.ts`, which `http.ts` and `report.ts` import. Say if you'd rather keep it private and divide by a literal.