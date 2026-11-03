`parseDuration` now returns milliseconds. All 12 tests pass and `tsc --noEmit` reports no errors.

Changes:
- **`src/duration.ts`**: unit table is now ms (`s: 1000`, `m: 60_000`, `h: 3_600_000`, `d: 86_400_000`). Doc comment updated.
- **Removed the `* 1000` multiplier** in `src/cache.ts`, `src/retry.ts` (`backoffDelayMs`) and `src/scheduler.ts` (`nextRun`).
- **`src/validate.ts`**: TTL bounds are now `MIN_TTL_MS = 5_000` and `MAX_TTL_MS = 86_400_000`, compared against the ms value.
- **Converted back to seconds where seconds are the contract**, so external output doesn't change:
  - `src/http.ts`: `Retry-After` header is `parseDuration(wait) / 1000`. The HTTP spec wants seconds.
  - `src/report.ts`: the `s` labels in `describeSettings` now print `/ 1000`.
- **`test/duration.test.ts`**: expected values updated to ms.

Decision for you: `Retry-After` and the report output still show seconds, since those are external formats. If you'd rather the report show ms, that's a one-line change.