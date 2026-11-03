`parseDuration` now returns milliseconds. All 12 tests pass and `tsc --noEmit` is clean.

**What changed**
- **`src/duration.ts`**: the lookup table is now in milliseconds and named `MS_PER_UNIT`. I added an exported `MS_PER_SECOND = 1000` so the number isn't written out in several places (G25). The doc comment now says milliseconds.
- **Callers that wanted milliseconds** (`cache.ts`, `retry.ts`, `scheduler.ts`): I removed the `* 1000`.
- **Callers that need seconds**, which would have broken silently:
  - **`http.ts`**: `Retry-After` must be in seconds, so it divides by `MS_PER_SECOND`.
  - **`report.ts`**: the summary prints values like `30s`, so it now converts through a small `durationInSeconds` helper. That avoids repeating the division (G5).
  - **`validate.ts`**: the TTL limits are now in milliseconds and come from `parseDuration("5s")` and `parseDuration("1d")`. The error messages use the same constants, so the limits and messages can't disagree.
- **`test/duration.test.ts`**: the expected values are now in milliseconds (e.g. `30_000`).

**Worth knowing**
- **External code may break:** `parseDuration` is exported from `src/index.ts`, so any code outside this repo that calls it will now get values 1000× larger. Whether that counts as a breaking release is your call.
- **Untested:** `http.ts` and `report.ts` have no tests, so the passing run doesn't check the two places that convert back to seconds. I checked them by reading the code. Tests for them would be cheap if you want them.