`parseDuration` now returns milliseconds, and every caller is adapted. `npm test` passes (12/12) and `npm run typecheck` is clean.

**Changes**

- **`src/duration.ts`**: the unit table now maps to milliseconds, built from an exported `MS_PER_SECOND = 1000` constant (G25). The function returns ms.
- **`src/cache.ts`**: dropped `* 1000` from `expiresAt`.
- **`src/scheduler.ts`**: dropped `* 1000` from `nextRun`.
- **`src/retry.ts`**: dropped `* 1000` from `backoffDelayMs`. The result is still ms, so `withRetry` is unchanged.
- **`src/validate.ts`**: the TTL bounds are now computed in ms via `parseDuration("5s")` and `parseDuration("1d")`, replacing the seconds constants. This also removes the magic `24 * 60 * 60`.
- **`src/http.ts`**: `Retry-After` is still whole seconds, so it now divides by `MS_PER_SECOND`.
- **`src/report.ts`**: the message still says seconds, so it divides by `MS_PER_SECOND` before formatting.
- **`test/duration.test.ts`**: expectations updated to ms (e.g. `"30s"` → `30_000`).

**Things to know**

- `parseDuration` is re-exported from `src/index.ts`, so this is a breaking change for any external consumer of the package. If you want, I can bump the major version or note it in a changelog.
- `cache.test.ts`, `retry.test.ts` and `scheduler.test.ts` needed no edits, since their observable behaviour (ms timestamps and sleep delays) is unchanged.
- I did not commit anything.