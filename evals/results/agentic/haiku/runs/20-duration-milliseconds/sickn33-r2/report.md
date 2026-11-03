`parseDuration` now returns milliseconds, and every caller uses that unit. All 12 tests pass and `tsc --noEmit` is clean. I didn't commit anything.

The conversion table is now in ms (`s: 1_000`, `m: 60_000`, `h: 3_600_000`, `d: 86_400_000`), and the doc comment says so.

Callers:
- **`cache.ts`, `scheduler.ts`, `retry.ts`**: dropped the `* 1000` multiplications.
- **`validate.ts`**: the TTL bounds are now `MIN_TTL_MS` / `MAX_TTL_MS` in ms, and the comparisons use ms. The error messages are unchanged.
- **`http.ts`** (`Retry-After`) and **`report.ts`**: these must still output seconds, so they divide by 1000. Output is unchanged.

Tests:
- `test/duration.test.ts` expectations are now ms.
- `test/retry.test.ts` changed only the `1m` case to `240_000`. The other expectations were already ms.

I didn't change `src/index.ts`, which re-exports `parseDuration`, so anything importing it from the package now gets ms. That is a public behavior change for consumers outside this repo.