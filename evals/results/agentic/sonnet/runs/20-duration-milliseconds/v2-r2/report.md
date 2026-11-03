`parseDuration` now returns milliseconds, and every caller is updated. Tests (12/12) and the typecheck pass.

- **`src/duration.ts`**: the unit table is now `MS_PER_UNIT` (`s: 1000` … `d: 86_400_000`), and the doc comment says milliseconds.
- **`cache.ts`, `retry.ts`, `scheduler.ts`**: removed the `* 1000`.
- **`validate.ts`**: the TTL bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`. The error messages are unchanged.
- **`http.ts`, `report.ts`**: these two need seconds, so they now divide by 1000. `Retry-After` has to be in seconds, and the settings description prints `s`.
- **`test/duration.test.ts`**: expected values changed to milliseconds.

`Retry-After` and the settings text are now seconds values computed with `/ 1000`. A duration like `"30s"` still gives `30`, as before.