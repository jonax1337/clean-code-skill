`parseDuration` now returns milliseconds, and every caller uses that value directly. The test suite passes (12/12) and the typecheck is clean.

**Changes**
- `src/duration.ts`: the unit table is now milliseconds (`s: 1_000` … `d: 86_400_000`), so the function returns ms.
- `src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`: removed the `* 1000`.
- `src/validate.ts`: TTL bounds are now `MIN_TTL_MS` / `MAX_TTL_MS`. Error messages are unchanged.
- `src/http.ts` and `src/report.ts`: these still output seconds, so they divide by 1000. `Retry-After` stays a whole number of seconds, and the report text is unchanged.
- `test/duration.test.ts`: expectations are now milliseconds. I ran it first and saw the expected failure (`30 !== 30000`).

**Behavior**: nothing user-visible changed. The retry, cache, scheduler, validation, HTTP header and report outputs are the same as before.

**Decisions for you**
- `src/index.ts` re-exports `parseDuration`, so any external consumer of the package now gets milliseconds. If that matters, a rename such as `parseDurationMs` would make the change explicit.
- I did not commit. The repo's rules only commit when asked, so the diff is staged in the working tree. Say the word and I'll commit it in one commit with the message and attribution line you specified.