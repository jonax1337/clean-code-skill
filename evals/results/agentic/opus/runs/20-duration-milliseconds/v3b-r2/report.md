`parseDuration` now returns milliseconds, and every caller has been updated to match.

**Changes:**
- **`src/duration.ts`**: the unit table is now in milliseconds. I also export a new `MS_PER_SECOND = 1000` constant.
- **`cache.ts`, `scheduler.ts`, `retry.ts`**: these wanted milliseconds already, so I just removed the `* 1000`.
- **Three callers actually need seconds.** Dropping the `* 1000` alone would have broken them:
  - `http.ts`: the `Retry-After` header must be in whole seconds, so it divides by `MS_PER_SECOND`.
  - `report.ts`: it prints values like `30s`. A small `seconds()` helper converts before printing.
  - `validate.ts`: the TTL limits were numbers in seconds (`5`, `24*60*60`). Now they're worked out with `parseDuration("5s")` and `parseDuration("1d")`, and the error messages use those same strings, so the limit and its message can't drift apart.

**Tests:**
- `test/duration.test.ts` now expects milliseconds (`30_000` and so on).
- I added `test/http.test.ts` and `test/report.test.ts`, because nothing tested the two places that convert back to seconds. Both pass on the original code and on the new code, so the output is unchanged.

**Results:**
- Before the change: `npm test` 12 passed, `npm run typecheck` clean.
- After the change: `npm test` 14 passed, 0 failed, and `npm run typecheck` clean.

**API change:** `parseDuration` is re-exported from `src/index.ts`, so any outside code that calls it will now get milliseconds instead of seconds. That's a breaking change and deserves a mention in the changelog or a version bump.

Nothing is committed yet.