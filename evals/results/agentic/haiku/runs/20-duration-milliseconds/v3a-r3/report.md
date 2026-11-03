`parseDuration` now returns milliseconds. Tests pass (12/12) and `tsc --noEmit` reports no errors.

Changes:
- **`src/duration.ts`**: unit table is now in ms (`s: 1000`, `m: 60_000`, …). The doc comment says ms.
- **Callers that multiplied by 1000 drop the multiplication:** `cache.ts`, `retry.ts`, `scheduler.ts`.
- **`src/validate.ts`**: the TTL bounds are now `MIN_TTL_MS` / `MAX_TTL_MS`, so they compare against ms. The error messages are unchanged.
- **Callers that need seconds divide by 1000:**
  - `http.ts`: `Retry-After` is defined in seconds, so the header value is unchanged.
  - `report.ts`: divides by 1000 so the output stays `timeout 30s, ttl 5m`, not raw milliseconds. If you'd rather the report show ms, that's a one-line change.
- **`test/duration.test.ts`**: expected values are now ms.

Decision for you: `parseDuration` is re-exported from `src/index.ts`, so any external consumer of the package will see the return value change from seconds to ms. I didn't add a changelog or a major-version bump. Nothing is committed.