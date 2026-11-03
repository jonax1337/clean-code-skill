`parseDuration` now returns milliseconds. The test suite passes (12/12) and `tsc --noEmit` reports no errors.

**Changes**
- `src/duration.ts`: the unit table is now in milliseconds, and the doc comment says so.
- `src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`: removed the `* 1000` multipliers, since the value is already in ms.
- `src/validate.ts`: the min and max TTL constants are now in ms (`5_000` and `86_400_000`). The error messages still say "5s" and "1d".
- `src/http.ts`: `Retry-After` is still whole seconds, so it now divides by 1000. All inputs are whole-second units, so the result is exact.
- `src/report.ts`: the output stays in seconds (`timeout 30s, ttl 300s`), so it divides by 1000. If you'd rather the report show milliseconds, that's a one-line change.
- `test/duration.test.ts`: expectations updated to ms.

`test/retry.test.ts` was left alone. It checks sleep values that come from `backoffDelayMs`, and those are still ms with the same results.

I haven't committed anything.