`parseDuration` now returns milliseconds. All 12 tests pass and `tsc --noEmit` is clean. Nothing is committed.

**Changes**

- **`src/duration.ts`**: the unit table is now milliseconds (`s: 1000`, `m: 60_000`, `h: 3_600_000`, `d: 86_400_000`). The doc comment says so.
- **Callers that multiplied by 1000 now don't:** `cache.ts`, `retry.ts` and `scheduler.ts`.
- **`validate.ts`**: the TTL bounds are now `MIN_TTL_MS = 5_000` and `MAX_TTL_MS = 86_400_000`. The error messages still say "5s" and "1d".
- **Callers that need seconds divide by 1000:**
  - `report.ts` still prints `timeout 30s, ttl 300s`, so its output is unchanged.
  - `http.ts` still sends `Retry-After` in whole seconds. Every unit is a whole number of seconds, so the division is exact.
- **`test/duration.test.ts`**: expected values are now in milliseconds. `retry.test.ts` and the scheduler tests needed no changes because their values were already in milliseconds.

**Decision for you:** `src/index.ts` re-exports `parseDuration`, so this is a breaking change for anyone who imports it from the package. I left the name as-is. If you'd rather make the break explicit, I can rename it to something like `parseDurationMs`.

I didn't add tests for the `report.ts` and `http.ts` seconds conversion. Those outputs are only checked by reading the code.