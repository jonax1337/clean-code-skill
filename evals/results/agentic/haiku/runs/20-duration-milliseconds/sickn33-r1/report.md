`parseDuration` now returns milliseconds, and every caller is adjusted. All 12 tests pass and `tsc --noEmit` is clean. The changes are uncommitted.

**Changes**

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so.
- **Callers that multiplied by 1000 (`cache.ts`, `retry.ts`, `scheduler.ts`)**: removed the multiplication.
- **`src/validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`. The error messages are unchanged.
- **Callers that need seconds (`http.ts`, `report.ts`)**: these divide by 1000. `Retry-After` is defined in seconds, and `report.ts` prints an `s` suffix, so their output stays the same.
- **`test/duration.test.ts`**: expectations are now milliseconds, written with numeric separators (`30_000`).

`src/index.ts` re-exports `parseDuration` unchanged, so anything importing it from the package now gets milliseconds. That is a behaviour change for external consumers, so it may need a changelog note or a major version bump if the package is published.

I did not commit anything. Do you want me to commit this?