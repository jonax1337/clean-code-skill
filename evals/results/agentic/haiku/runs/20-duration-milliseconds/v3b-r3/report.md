`parseDuration` now returns milliseconds, and every caller uses that unit. Tests pass (12/12) and the typecheck is clean.

**Changes**
- `src/duration.ts`: the unit table now holds milliseconds. I exported a `MS_PER_SECOND` constant so the two places that need seconds don't hard-code `1000`.
- Callers that wanted milliseconds dropped their `* 1000`: `cache.ts`, `retry.ts`, `scheduler.ts`.
- `src/validate.ts`: the TTL bounds are now milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages are unchanged.
- Callers that need seconds now divide by `MS_PER_SECOND`: `http.ts` (`Retry-After`) and `report.ts` (the `s` labels). Their output is the same as before.
- `test/duration.test.ts`: expectations are in milliseconds.

**Verification**
- `npm test`: 12 pass, 0 fail, both before and after the change.
- `npm run typecheck`: exit 0.
- The existing tests don't cover `http`, `report`, `retry`, `scheduler` or `cache`. I ran a temporary script against each one and checked the results: `Retry-After: 120` for `2m`, `timeout 30s, ttl 3600s`, a retry backoff of 8000 ms for `1s` at attempt 3, a next run of 61000 for a 1m job, cache expiry at exactly 10 s, and the TTL bounds. I deleted the script afterwards.

**Things to know**
- `src/index.ts` re-exports `parseDuration`, so this is a breaking change for anyone importing it from the package. I didn't add a version bump or changelog entry.
- Nothing is committed; the changes are in the working tree.