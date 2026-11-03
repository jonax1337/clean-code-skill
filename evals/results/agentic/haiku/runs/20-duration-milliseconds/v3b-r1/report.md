`parseDuration` now returns milliseconds. Typecheck and the test suite pass: `tsc --noEmit` exited 0, and `node --test` reports 12 passed, 0 failed.

I changed these files:

- **`src/duration.ts`**: unit table is now in ms, and the doc comment says so.
- **Callers that wanted ms** (`cache.ts`, `retry.ts`, `scheduler.ts`): dropped the `* 1000`.
- **Callers that wanted seconds** (`http.ts`, `report.ts`): divide by 1000 at the call site, so `Retry-After` and the report text are unchanged. The input regex only allows whole units of a second or more, so the division is exact.
- **`src/validate.ts`**: the min/max bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`. The error messages still say "5s" and "1d".
- **`test/duration.test.ts`**: expectations now in ms.

Things to know:

- `parseDuration` is re-exported from `src/index.ts`, so anyone importing it from the package gets ms now. That is a breaking change for external consumers, and it is worth a changelog note or a major version bump if this is published.
- `http.ts` and `report.ts` have no direct tests. I checked their output by reading the code, not by running it.
- I did not commit anything.