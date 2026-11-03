`parseDuration` now returns milliseconds, and the call sites are adjusted to match. The test suite passes (12/12) and `tsc --noEmit` runs with no errors.

Changes:
- **`src/duration.ts`**: returns `… * 1000`, and the doc comment now says milliseconds.
- **`src/cache.ts`**, **`src/scheduler.ts`**, **`src/retry.ts`**: dropped the `* 1000`, since the value is already in ms.
- **`src/validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparison is in ms. The error messages are unchanged.
- **`src/http.ts`**: `Retry-After` is still whole seconds, so it's `parseDuration(wait) / 1000`.
- **`src/report.ts`**: the output still shows seconds, so each value is divided by 1000. The text stays the same.
- **`test/duration.test.ts`**: expected values are now in ms.

Two things to check:
- `parseDuration` is re-exported from `src/index.ts`, so anyone importing it from the package gets ms now. That's a breaking change for external callers if the package is published.
- `report.ts` still prints seconds. If you'd rather it print ms, that's a one-line change.