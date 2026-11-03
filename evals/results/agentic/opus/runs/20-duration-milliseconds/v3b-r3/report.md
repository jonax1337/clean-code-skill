`parseDuration` now returns milliseconds, and the rest of the code is updated to match.

**Changes**
- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so. I exported a new `MS_PER_SECOND = 1000` so callers that need seconds don't repeat the number 1000.
- **`cache.ts`, `retry.ts`, `scheduler.ts`**: removed the `* 1000`.
- **Three files that would have broken without an error**, because they used the result as seconds:
  - `http.ts`: `Retry-After` has to be in whole seconds, so it now divides by `MS_PER_SECOND`. Every unit is a whole number of seconds, so the result stays a whole number.
  - `report.ts`: it prints values like `300s`, so it now divides by `MS_PER_SECOND` too.
  - `validate.ts`: the limits are now `MIN_TTL_MS` and `MAX_TTL_MS` and the comparisons use milliseconds. Without this, every TTL would have failed with "exceeds the maximum".
- **`test/duration.test.ts`**: expected values are now in milliseconds.

**New tests:** none of the three files above had tests for this, so before changing anything I added tests that pin their current behavior and ran them against the original code. They are `test/http.test.ts`, `test/report.test.ts`, and two new cases in `test/validate.test.ts` (the minimum, and both limits being accepted).

**Results**
- `npm test`: 16 passed, 0 failed, both before and after the change.
- `tsc --noEmit`: no errors.

**Breaking change:** `parseDuration` is exported from `src/index.ts`, so any code outside this repo that calls it will now get milliseconds instead of seconds.

I haven't committed anything.