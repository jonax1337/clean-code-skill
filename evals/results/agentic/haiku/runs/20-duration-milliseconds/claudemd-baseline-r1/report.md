`parseDuration` now returns milliseconds. All 14 tests pass and `tsc --noEmit` is clean.

**Changes**

- `src/duration.ts`: the unit table is now milliseconds (`s: 1000`, `m: 60_000`, `h: 3_600_000`, `d: 86_400_000`), and the doc comment says so.
- `src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`: removed the `* 1000` multiplications.
- `src/validate.ts`: the min/max TTL bounds are now in milliseconds (`MIN_TTL_MS = 5_000`, `MAX_TTL_MS = 86_400_000`), so the comparisons still mean 5s and 1d.
- `src/http.ts`: `Retry-After` is still whole seconds, so it now divides by 1000.
- `src/report.ts`: the message now shows milliseconds, with the `ms` suffix instead of `s`. If you'd rather keep the old `30s` output, dividing by 1000 there is a one-line change.
- `test/duration.test.ts` and `test/retry.test.ts`: expectations updated to milliseconds.
- New `test/http.test.ts` and `test/report.test.ts`: these cover the two conversions that had no tests before.

Nothing is committed.