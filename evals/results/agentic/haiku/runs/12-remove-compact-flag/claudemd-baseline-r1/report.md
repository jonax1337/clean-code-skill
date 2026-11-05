`--compact` is removed and `cargo test` passes: 13 unit tests and 12 integration tests, no failures.

Changes:
- **`src/cli.rs`**: removed the `compact` option field, its default, the `-c`/`--compact` parser arm (including the deprecation warning), its usage line, and its unit test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact`, `trim_cells`, and their two tests.
- **`tests/cli.rs`**: replaced the three compact integration tests with one test asserting that `--compact` now returns `UnknownOption`.
- **`README.md`**: removed the `-c, --compact` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased.

Behavior change: `--compact` and `-c` now fail with "unknown option" instead of printing a deprecation warning and working. Anyone still passing them will get an error on upgrade. I did not commit the changes.