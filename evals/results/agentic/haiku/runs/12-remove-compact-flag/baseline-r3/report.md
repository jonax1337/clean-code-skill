I removed `--compact` (`-c`) and its code, and the test suite still passes: 13 unit tests and 11 integration tests. The build has no warnings.

Changes:
- **`src/cli.rs`**: removed the flag from the usage text, the `compact` field on `Options`, the parse arm (with its deprecation warning), and its unit test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact` and `trim_cells`, which only it used, and its two tests.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the options-table row.
- **`CHANGELOG.md`**: added a `Removed` entry under Unreleased, noting that `-c` now fails as an unknown option and pointing to `--max-width`.

Passing `-c` or `--compact` now returns the normal unknown-option error. I did not add a test for that. The existing `rejects_unknown_options` test covers the same path.

I haven't committed anything.