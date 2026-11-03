`--compact` is removed. The full suite passes and the build has no warnings.

The tests that check `--compact` behavior were deleted along with the feature, since they would fail otherwise. That's six tests: one in `src/cli.rs`, two in `src/render.rs`, and three in `tests/cli.rs`. The remaining tests are unchanged.

Changes:
- **`src/cli.rs`:** removed the `compact` field and its default, the `-c`/`--compact` arm with its deprecation warning, and the usage line.
- **`src/render.rs`:** removed the compact branch in `render_table`, plus `render_compact` and its helper `trim_cells`.
- **`README.md`:** removed the options-table row.
- **`CHANGELOG.md`:** added a `### Removed` entry under Unreleased. It notes that `-c` now fails with an unknown-option error and points to `--max-width`.

Test results: 13 unit tests and 11 integration tests pass, down from 14 integration tests before, which matches the six deleted.

Behavior change: `-c` and `--compact` now return an unknown-option error instead of printing a warning and continuing. Any scripts that still pass them will fail.

I haven't committed anything.