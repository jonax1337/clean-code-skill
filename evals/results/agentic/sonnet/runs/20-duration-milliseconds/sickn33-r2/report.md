`parseDuration` now returns milliseconds, and all 12 tests pass. I didn't run `tsc --noEmit`.

- **`src/duration.ts`**: the unit table is now `MILLISECONDS_PER_UNIT`, and the doc comment says milliseconds.
- **`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`**: I removed the `* 1000`.
- **`src/validate.ts`**: the TTL min and max constants and the local variable are now in milliseconds. The error messages are unchanged.
- **`src/http.ts`, `src/report.ts`**: these need seconds (the `Retry-After` header and the `…s` text), so they now divide by 1000.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

`parseDuration` is also exported from `src/index.ts`, so any code outside this repo that calls it will now get values 1000× larger.