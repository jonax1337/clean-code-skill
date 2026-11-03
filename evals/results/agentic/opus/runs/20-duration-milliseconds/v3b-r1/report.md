`parseDuration` now returns milliseconds, and every caller has been updated.

**Changes**
- **`src/duration.ts`**: the unit table is now in milliseconds and the doc comment says so. I also export a new constant, `MS_PER_SECOND`, so callers don't need a bare `1000`.
- **Callers that wanted milliseconds** (`cache.ts`, `retry.ts`, `scheduler.ts`): I removed the `* 1000`.
- **Callers that actually wanted seconds**: simply dropping the `* 1000` would have broken these without any error, so each one now converts back:
  - `http.ts`: the `Retry-After` header must be in whole seconds, so it divides by `MS_PER_SECOND`. The result is always a whole number because the parser only accepts whole numbers of s/m/h/d.
  - `report.ts`: it prints values with an `s` suffix, so it also divides by `MS_PER_SECOND`.
  - `validate.ts`: the min/max bounds are now `MIN_TTL_MS` and `MAX_TTL_MS`, compared in milliseconds directly.
- **Tests**: the expected values in `test/duration.test.ts` are now in milliseconds. Before changing anything, I added tests that record the current behaviour of the seconds-based callers, since none of them were tested at the edges: `test/http.test.ts`, `test/report.test.ts`, and the min and boundary cases in `test/validate.test.ts`. They passed against the old code and still pass now.

**Checks**
- `npm test`: 16 passed, 0 failed.
- `npm run typecheck`: no errors.

**Note:** `parseDuration` is re-exported from `src/index.ts`, so it's part of the public API. Any outside code that calls it will now get values 1000× larger. Inside this repo every caller is updated, but this is a breaking change for anyone else who uses it. Nothing is committed yet.