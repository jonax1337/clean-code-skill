`parseDuration` now returns milliseconds, and every caller uses that unit. The test suite passes (12/12) and `tsc --noEmit` reports no errors.

Changes:
- **`src/duration.ts`**: returns milliseconds. The unit table is now in ms, and I exported a `MS_PER_SECOND` constant so the seconds-based callers don't need a bare `1000`.
- **`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`**: removed the `* 1000`, since they already want milliseconds.
- **`src/validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`. The error messages are unchanged.
- **`src/http.ts`, `src/report.ts`**: these still output seconds, so they divide by `MS_PER_SECOND`. The `Retry-After` header and the `timeout …s, ttl …s` text are the same as before.
- **`test/duration.test.ts`**: expected values are now in milliseconds.

Decision for you: `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for any package consumer that relied on seconds. I didn't add a changelog entry or a major version bump. Say if you want either.

I haven't committed anything.