`parseDuration` now returns milliseconds, and every caller uses that value directly. All 12 tests pass.

Changes:
- **`src/duration.ts`**: multiplies by 1000 at the end and the doc comment says milliseconds.
- **`src/cache.ts`**, **`src/scheduler.ts`**, **`src/retry.ts`**: removed the `* 1000`.
- **`src/validate.ts`**: the TTL bounds are now in milliseconds (`MIN_TTL_MS`, `MAX_TTL_MS`). The error messages still say "5s" and "1d".
- **`src/http.ts`**: `Retry-After` is still whole seconds, so it divides by 1000.
- **`src/report.ts`**: the output still reads in seconds, so it divides by 1000.
- **`test/duration.test.ts`**: expected values are now milliseconds.

`npm test` passes 12/12. `npm run typecheck` printed no errors, but my command piped through `tail`, so I didn't capture tsc's own exit code.

`parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for anyone importing it from the package. Say if you want a note in a changelog or a major version bump.