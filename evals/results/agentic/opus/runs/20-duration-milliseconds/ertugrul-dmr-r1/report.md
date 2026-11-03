`parseDuration` now returns milliseconds. All 16 tests pass and `tsc --noEmit` reports no errors. I haven't committed anything.

**Callers that already wanted milliseconds:** I removed the `* 1000` from `src/cache.ts`, `src/retry.ts` and `src/scheduler.ts`. Their results are the same as before.

**Callers that need seconds:** three places used the return value as seconds. Simply dropping a multiplication elsewhere would have quietly broken them:
- **`src/http.ts`**: `Retry-After` has to be in whole seconds, so it now divides by `MS_PER_SECOND`. Durations only come in whole units of a second or more, so the header value is still a whole number.
- **`src/report.ts`**: it prints values with an `s` suffix, so it converts back to seconds through a small `durationInSeconds` helper.
- **`src/validate.ts`**: the limits used to be `MIN_TTL_SECONDS = 5` and `MAX_TTL_SECONDS = 86400`. They're now worked out from `"5s"` and `"1d"` with `parseDuration`. The error messages use those same strings, so the limits and the messages can't drift apart (G5).

**Other changes:**
- `src/duration.ts` now exports `MS_PER_SECOND`, and the unit table is written out in milliseconds. This replaces magic numbers like `86400` (G25).
- I updated the expected values in `test/duration.test.ts` to milliseconds.
- I added tests: the TTL minimum and maximum limits (`4s` is rejected, `5s` and `1d` are accepted) in `test/validate.test.ts`, and the `Retry-After` header and the settings report in a new `test/report_http.test.ts`. These are the places where unit mistakes would be most likely (T5).

One thing to watch: `parseDuration` is part of the public API through `src/index.ts`. Any code outside this repo that calls it will now get milliseconds instead of seconds.