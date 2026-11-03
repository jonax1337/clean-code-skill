`parseDuration` now returns milliseconds, and every caller uses that value directly.

**Changes**
- `src/duration.ts`: the unit table is now milliseconds, and the doc comment says so.
- `src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`: removed the `* 1000`.
- `src/validate.ts`: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`. The error messages are unchanged.
- `src/http.ts`: `Retry-After` is defined in seconds, so it now divides by 1000. The header value is the same as before.
- `src/report.ts`: divides by 1000, so the output still reads `timeout 30s, ttl 300s`.
- `test/duration.test.ts`: expectations updated to milliseconds.

**Verification**
- `npm test`: 12 of 12 pass. The retry, cache and scheduler tests also pass, so the removed multipliers are covered.
- `npx tsc --noEmit`: no errors reported.

**Things to know**
- `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for anyone importing it from the package. Bump the version or note it in the changelog if you publish.
- I left the display format in `report.ts` as seconds. If you'd rather it print milliseconds, that's a one-line change, but it would alter the output.
- I didn't commit anything.