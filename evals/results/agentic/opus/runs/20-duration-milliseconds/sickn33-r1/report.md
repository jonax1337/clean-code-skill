`parseDuration` now returns milliseconds. All 12 tests pass and the typecheck is clean.

**Callers that wanted milliseconds:** I removed the `* 1000` from these.
- `src/cache.ts`: TTL expiry
- `src/retry.ts`: `backoffDelayMs`
- `src/scheduler.ts`: `nextRun`

**Callers that need seconds:** these were already correct because they used the old seconds value directly. Without a change they would have broken without any error, so I adapted them:
- `src/http.ts`: the `Retry-After` header must be in whole seconds, so it now uses `Math.ceil(ms / 1000)`. Otherwise `"30s"` would have sent `Retry-After: 30000`.
- `src/report.ts`: `describeSettings` prints values with an `s` suffix. It now converts back to seconds with a small helper, `durationInSeconds`, so the output is unchanged.
- `src/validate.ts`: the min/max TTL limits are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). Without this, `"1m"` would have counted as exceeding the 1-day maximum.

**Tests:** I changed the expected values in `test/duration.test.ts` to milliseconds. The other tests passed without changes. However, none of them cover `http.ts` or `report.ts`, so the existing tests would not have caught a mistake in those two files.

**Public API:** `src/index.ts` re-exports `parseDuration`, so code outside this repo that uses it will now get values 1000× larger. If you have outside users, treat this as a breaking change. Renaming the function to `parseDurationMs` would make the new unit obvious at each call site; I can do that if you want.

I haven't committed anything.