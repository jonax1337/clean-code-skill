`parseDuration` now returns milliseconds, and I've updated every caller. All 12 tests pass and the typecheck is clean.

**Callers that wanted milliseconds** no longer multiply by 1000:
- `src/cache.ts`: the expiry time.
- `src/retry.ts`: `backoffDelayMs`.
- `src/scheduler.ts`: `nextRun`.

**Callers that wanted seconds** would have silently become 1000× off, so these needed real changes:
- `src/http.ts`: the `Retry-After` header must be in whole seconds, so it now divides by 1000 and rounds up.
- `src/report.ts`: the text still shows `…s`, so both values are divided by 1000 there.
- `src/validate.ts`: the TTL minimum and maximum (5s and 1 day) are now stored in milliseconds (`MIN_TTL_MS` / `MAX_TTL_MS`), so the checks still compare like with like.

**Tests:** I updated the expected values in `test/duration.test.ts` to milliseconds.

`src/index.ts` re-exports `parseDuration`, so this is a breaking change for anyone who imports it from the package. If that matters, it needs a version bump and a changelog note.