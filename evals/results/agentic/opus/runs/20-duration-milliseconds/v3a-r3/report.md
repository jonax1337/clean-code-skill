`parseDuration` now returns milliseconds. I updated all six callers, and tests and the type check pass.

**Callers that wanted milliseconds:** I removed the `* 1000` from `cache.ts`, `retry.ts` and `scheduler.ts`.

**Callers that need seconds:** three places had used the seconds value directly, and these would have broken without a change:
- `http.ts`: the `Retry-After` header must be in seconds, so it now divides by 1000. The parser only accepts whole s/m/h/d values, so the result is always a whole number.
- `report.ts`: the text still shows seconds ("timeout 30s"), so it divides by 1000.
- `validate.ts`: the min/max TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`), so they compare directly with the parsed value. The error messages are unchanged.

**`duration.ts`:** the unit table is now built from a new exported `MS_PER_SECOND` constant, which the three seconds callers use instead of a bare `1000`.

**Tests:** none of the three seconds callers had tests. So before changing anything, I added tests that record their current behaviour: `test/http.test.ts`, `test/report.test.ts`, and checks in `test/validate.test.ts` for the minimum and for the exact limits. They passed on the old code and still pass now, which shows those callers behave the same. I also changed the expected values in `test/duration.test.ts` to milliseconds.

**Results:**
- `npm test`: 16 passed, 0 failed (12 before, plus my 4 new ones)
- `npm run typecheck`: no errors

**Breaking change:** `parseDuration` is exported publicly from `src/index.ts`. Any outside code that calls it will now get values 1000× larger. If other projects use this package, it needs a major version bump or a note in the changelog. I haven't changed the version number.