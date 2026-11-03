`parseDuration` now returns milliseconds. Tests and the type check pass.

**What changed**
- `src/duration.ts`: the unit table is now in milliseconds, built from a new exported `MS_PER_SECOND = 1000`, and the doc comment says milliseconds.
- `cache.ts`, `retry.ts`, `scheduler.ts`: the `* 1000` multiplications are gone.
- Three callers actually need seconds, so they convert back instead:
  - `http.ts`: `Retry-After` must be whole seconds, so it divides by `MS_PER_SECOND`. Durations only accept whole numbers, so the result is still a whole number.
  - `report.ts`: the text still prints seconds (`timeout 30s, ttl 300s`). It uses a small private `inSeconds` helper.
  - `validate.ts`: the limits are now `MIN_TTL_MS = parseDuration("5s")` and `MAX_TTL_MS = parseDuration("1d")`. Each limit now matches the `5s`/`1d` wording in its error message.
- `test/duration.test.ts`: the expected values are now in milliseconds.

**Tests:** `http.ts`, `report.ts` and the TTL minimum had no tests, which is where a missed conversion would have gone unnoticed. Before changing anything I added tests for them (`test/http.test.ts`, `test/report.test.ts`, and the below-minimum and accepted-boundary cases in `test/validate.test.ts`). They passed against the original code.

**Commands run after the change**
- `npm test`: 16 tests, 16 passed, 0 failed (12 before plus 4 new)
- `npx tsc --noEmit`: no errors

**Breaking change:** `parseDuration` is exported from `src/index.ts`, so any code outside this repo that calls it will now get values 1000× larger. Inside the repo every caller is updated. If the package is used elsewhere, bump the major version.

I haven't committed anything.