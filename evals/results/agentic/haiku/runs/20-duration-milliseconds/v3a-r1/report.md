`parseDuration` now returns milliseconds, and the callers are adapted. All 12 tests pass and `tsc --noEmit` is clean.

**Changes**
- `src/duration.ts`: unit table is now in ms (`s: 1_000`, `m: 60_000`, …), and the doc comment says ms.
- Callers that wanted ms had their `* 1000` removed: `cache.ts`, `scheduler.ts`, `retry.ts` (`backoffDelayMs`).
- Callers that need seconds now divide by 1000, so their output is unchanged:
  - `http.ts`: `Retry-After` header, which the HTTP spec defines in seconds.
  - `report.ts`: the `timeout …s, ttl …s` text.
- `validate.ts`: the min/max TTL constants are now in ms (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages are unchanged.
- `test/duration.test.ts`: expected values updated to ms.

**Things to know**
- `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for any external consumer that relied on seconds. If this is a published package, it may warrant a major version bump or a changelog note.
- I did not run the `validate.ts` or `http.ts` paths through a test of their own. Nothing in the suite covers `validateTtl`, `rateLimitHeaders` or `describeSettings`, so their behavior is verified by reading, not by tests.