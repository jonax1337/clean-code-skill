`parseDuration` now returns milliseconds. The test suite passes (12/12) and the type check runs clean.

**Changes**

- `src/duration.ts`: the unit table is now milliseconds (`MS_PER_UNIT`), and the doc comment says so.
- Callers that wanted milliseconds drop their `* 1000`: `cache.ts`, `retry.ts`, `scheduler.ts`.
- Callers that need seconds divide by 1000 at the boundary, so their output doesn't change:
  - `http.ts`: the `Retry-After` header stays in whole seconds.
  - `report.ts`: the `timeout …s, ttl …s` string is unchanged.
- `validate.ts`: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the comparison is in milliseconds. The error messages are unchanged.
- `test/duration.test.ts`: expected values updated to milliseconds.

**Verification**

- `npm test`: 12 pass, 0 fail.
- `npm run typecheck`: no errors reported.

**Gaps**

- No test covers `report.ts` or `http.ts`, so I checked their output by reading the code only. The string and header values should be the same as before. I did not add tests for them, since that would widen the change.
- `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for any external consumer that expects seconds. I left the version alone; a major bump or changelog note may be warranted.
- `Retry-After` now relies on `ms / 1000` being an integer. That holds because the parser only accepts whole-number units.