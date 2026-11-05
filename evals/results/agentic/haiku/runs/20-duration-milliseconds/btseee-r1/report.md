`parseDuration` now returns milliseconds. The test suite passes (12/12) and the typecheck is clean.

**Changes**

- `src/duration.ts`: the unit table now maps to milliseconds (`s: 1000`, … `d: 86_400_000`), and the doc comment says so.
- `src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`: dropped the `* 1000` multiplier, since the value is already in ms.
- `src/validate.ts`: the TTL bounds are now `MIN_TTL_MS = 5_000` and `MAX_TTL_MS = 86_400_000`, so the comparison happens directly in ms. The error messages still say "5s" and "1d".
- `src/http.ts` and `src/report.ts`: these output seconds (`Retry-After` is whole seconds, and the report text ends in `s`), so they now divide by 1000. Their output is unchanged.
- `test/duration.test.ts`: the expected values are now ms.

**Things to be aware of**

- `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for anyone importing it from the package. If the package is published or used outside this repo, that may warrant a major version bump or a changelog note.
- I did not commit anything.