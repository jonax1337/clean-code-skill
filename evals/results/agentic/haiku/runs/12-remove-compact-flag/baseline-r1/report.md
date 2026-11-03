I removed `--compact` (and its short form `-c`) and the tests still pass: 14 unit tests and 12 integration tests, with no warnings.

What changed:
- **`src/cli.rs`**: removed the flag, the `compact` field, its help line, and the deprecation warning. Passing `--compact` or `-c` now fails with `UnknownOption`.
- **`src/render.rs`**: removed the compact branch, `render_compact`, `trim_cells`, and their two tests.
- **`tests/cli.rs`**: replaced the three compact tests with one test asserting that `--compact` is rejected.
- **`README.md`**: removed the `-c, --compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased.

Choices I made:
- I kept a test that the flag is rejected, so a future change can't quietly bring it back.
- I used a "Removed" changelog heading rather than folding it into "Deprecated".

Nothing is committed. Anyone still passing `--compact` will get an error, not a warning, so this is a breaking change for them.