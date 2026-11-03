`parseDuration` now returns milliseconds, and every caller is adjusted. All 12 tests pass and `tsc --noEmit` is clean.

Changes:
- **`src/duration.ts`**: the unit table is now milliseconds (`s: 1000`, `m: 60_000`, `h: 3_600_000`, `d: 86_400_000`). The doc comment says ms.
- **Callers that multiplied by 1000 no longer do:**
  - `cache.ts`: `expiresAt` uses the ms value directly.
  - `retry.ts`: `backoffDelayMs` is `parseDuration(base) * 2 ** attempt`.
  - `scheduler.ts`: `nextRun` is `lastRun + parseDuration(every)`.
- **Callers that needed seconds now divide by 1000:**
  - `http.ts`: `Retry-After` header.
  - `report.ts`: the `timeout …s, ttl …s` text, so its output is unchanged.
- **`validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS` and are compared against the ms value. The error messages are unchanged.
- **`test/duration.test.ts`**: expected values are in ms.

Decision for you: `parseDuration` is re-exported from `src/index.ts`, so external consumers of the package will see the new unit. That is the intended breaking change, but it may warrant a version bump or changelog entry.