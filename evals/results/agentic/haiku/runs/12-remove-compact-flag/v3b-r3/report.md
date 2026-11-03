`--compact` / `-c` is removed, and `cargo test` passes after the change: 13 unit tests and 12 integration tests, with no warnings.

What changed:
- **`src/cli.rs`**: removed the flag from the usage text, the `Options` struct and its default, the parser arm (including the deprecation warning), and its unit test. `-c` and `--compact` now fall through to the existing "unknown option" error.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact` and `trim_cells`, which were only used by it, and their two unit tests.
- **`tests/cli.rs`**: replaced the three compact tests with one test asserting that `--compact` and `-c` return `UnknownOption`. I chose that over deleting the tests outright so the removal is pinned.
- **`README.md`**: removed the `-c` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased that points users to `--max-width`.

The only remaining mentions of "compact" are the changelog entries for 0.8.0 and the new removal note. I did not commit anything.