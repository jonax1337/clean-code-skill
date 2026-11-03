`--compact` / `-c` is removed, and `cargo test` passes: 13 unit tests and 11 integration tests, with no build warnings.

Changes:
- **`src/cli.rs`**: removed the `compact` field, its default, the `-c`/`--compact` parsing (with its deprecation warning), the help line, and the unit test.
- **`src/render.rs`**: removed the compact branch, `render_compact`, `trim_cells`, and their two tests.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the option row.
- **`CHANGELOG.md`**: added a `Removed` entry under Unreleased.

Running `-c` now fails with `tabulate: unknown option `-c`` and exit code 2. The CHANGELOG entry is the only place this is recorded for users. I did not commit anything.