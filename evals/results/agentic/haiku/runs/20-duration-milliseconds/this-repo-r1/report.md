`parseDuration` now returns milliseconds. All 12 tests pass and the type check printed no errors.

**Changes**
- `src/duration.ts`: the unit table now holds milliseconds, and the function returns ms. Its doc comment says so.
- Callers that multiplied by 1000 no longer do: `cache.ts`, `scheduler.ts`, and `retry.ts` (`backoffDelayMs`).
- Callers that need seconds now divide by 1000 explicitly:
  - `report.ts` keeps its existing "timeout 30s" output.
  - `http.ts` keeps `Retry-After` in whole seconds, as the HTTP spec requires.
- `src/validate.ts`: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparison is in ms. The error messages are unchanged.
- `test/duration.test.ts`: expectations are in ms.

**Verification**
- `npm test`: 12 pass, 0 fail.
- `npm run typecheck`: no errors printed. I did not capture its exit code.

**Things to know**
- `parseDuration` is re-exported from `src/index.ts`, so any external consumer of the package now gets milliseconds. This is a breaking change for them. I left the export alone; a major version bump or a changelog note may be warranted.
- No tests cover `report.ts`, `http.ts`, or the cache and scheduler TTL math beyond the existing tests. I checked those paths by reading the code, not by running them.
- I haven't committed anything.