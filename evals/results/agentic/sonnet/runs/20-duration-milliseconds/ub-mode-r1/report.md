`parseDuration` now returns milliseconds, and the callers are adapted. The 12 tests pass and `tsc --noEmit` is clean. I didn't run the crapper, dryer or mutator tools from the skill.

**Log**
1. I changed the expectations in `test/duration.test.ts` to milliseconds first. I didn't capture the failing run; the first test output I looked at was the passing one after the source edits.
2. `src/duration.ts`: the unit table is now `MS_PER_UNIT` with millisecond values, and the doc comment says milliseconds.
3. `src/cache.ts`, `src/scheduler.ts` and `src/retry.ts`: removed the `* 1000`, since they already wanted milliseconds.
4. `src/http.ts` and `src/report.ts`: these need seconds, so they now divide by 1000. `Retry-After` and the `…s` text output are unchanged.
5. `src/validate.ts`: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, so the comparison happens in milliseconds. The error messages are unchanged.
6. I committed everything as one commit.

No tests cover `http`, `report` or the minimum-TTL check, so I only checked those edits by reading them and by the type check.

I didn't push. The repo has no remote configured, so the commit is local only on `main`.